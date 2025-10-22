"""
Local File Manager Agent - Backend API
A Flask-based REST API for file system operations with LLM-powered function calling.

Author: Generated with AI assistance
License: MIT
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pathlib
from datetime import datetime
from typing import List, Dict, Any
import json
import ollama

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
BASE_PATH = os.path.expanduser("~")  # Default to user's home directory
MAX_FILE_SIZE_DISPLAY = 100  # Maximum number of files to return
OLLAMA_MODEL = "llama3.1:8b"  # Model with function calling support


class FileOperations:
    """Handle all file system operations with proper error handling."""

    @staticmethod
    def find_files_by_extension(directory: str, extension: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Find files by extension in a directory and its subdirectories.

        Args:
            directory: Starting directory path
            extension: File extension to search for (e.g., '.py', '.txt')
            limit: Maximum number of files to return

        Returns:
            List of file information dictionaries
        """
        try:
            files = []
            extension = extension if extension.startswith('.') else f'.{extension}'

            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    if filename.endswith(extension):
                        filepath = os.path.join(root, filename)
                        try:
                            stat = os.stat(filepath)
                            files.append({
                                'path': filepath,
                                'name': filename,
                                'size': stat.st_size,
                                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                'readable_size': FileOperations._format_size(stat.st_size)
                            })
                        except (OSError, PermissionError):
                            continue

                        if len(files) >= limit:
                            break
                if len(files) >= limit:
                    break

            return sorted(files, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            raise Exception(f"Error finding files: {str(e)}")

    @staticmethod
    def get_largest_files(directory: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the largest files in a directory tree.

        Args:
            directory: Starting directory path
            limit: Number of largest files to return

        Returns:
            List of file information dictionaries sorted by size
        """
        try:
            files = []

            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    try:
                        stat = os.stat(filepath)
                        files.append({
                            'path': filepath,
                            'name': filename,
                            'size': stat.st_size,
                            'readable_size': FileOperations._format_size(stat.st_size),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
                    except (OSError, PermissionError):
                        continue

            # Sort by size and return top N
            files.sort(key=lambda x: x['size'], reverse=True)
            return files[:limit]
        except Exception as e:
            raise Exception(f"Error getting largest files: {str(e)}")

    @staticmethod
    def create_folder(directory: str, folder_name: str) -> Dict[str, Any]:
        """
        Create a new folder in the specified directory.

        Args:
            directory: Parent directory path
            folder_name: Name of the folder to create

        Returns:
            Dictionary with creation status and path
        """
        try:
            new_path = os.path.join(directory, folder_name)

            if os.path.exists(new_path):
                return {
                    'success': False,
                    'message': f'Folder already exists: {new_path}',
                    'path': new_path
                }

            os.makedirs(new_path, exist_ok=False)
            return {
                'success': True,
                'message': f'Folder created successfully',
                'path': new_path
            }
        except Exception as e:
            raise Exception(f"Error creating folder: {str(e)}")

    @staticmethod
    def list_directory(directory: str) -> Dict[str, Any]:
        """
        List contents of a directory.

        Args:
            directory: Directory path to list

        Returns:
            Dictionary with files and folders
        """
        try:
            if not os.path.exists(directory):
                raise Exception(f"Directory does not exist: {directory}")

            items = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                try:
                    stat = os.stat(item_path)
                    items.append({
                        'name': item,
                        'path': item_path,
                        'is_directory': os.path.isdir(item_path),
                        'size': stat.st_size if not os.path.isdir(item_path) else 0,
                        'readable_size': FileOperations._format_size(stat.st_size) if not os.path.isdir(item_path) else '-',
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except (OSError, PermissionError):
                    continue

            return {
                'directory': directory,
                'items': sorted(items, key=lambda x: (not x['is_directory'], x['name']))
            }
        except Exception as e:
            raise Exception(f"Error listing directory: {str(e)}")

    @staticmethod
    def move_files(source_directory: str, destination_directory: str, pattern: str) -> Dict[str, Any]:
        """
        Move files matching a pattern from source to destination directory.

        Args:
            source_directory: Directory containing files to move
            destination_directory: Directory where files should be moved
            pattern: File pattern to match (e.g., 'Screenshot*.png', '*.txt')

        Returns:
            Dictionary with operation results and count of moved files
        """
        try:
            import glob
            import shutil

            # Validate directories
            if not os.path.exists(source_directory):
                raise Exception(f"Source directory does not exist: {source_directory}")

            if not os.path.exists(destination_directory):
                # Create destination directory if it doesn't exist
                os.makedirs(destination_directory, exist_ok=True)

            # Build the full pattern path
            search_pattern = os.path.join(source_directory, pattern)

            # Find matching files
            matching_files = glob.glob(search_pattern)

            if not matching_files:
                return {
                    'success': True,
                    'message': f'No files found matching pattern: {pattern}',
                    'moved_count': 0,
                    'files': []
                }

            moved_files = []
            errors = []

            for source_path in matching_files:
                # Only move files, not directories
                if os.path.isfile(source_path):
                    try:
                        filename = os.path.basename(source_path)
                        dest_path = os.path.join(destination_directory, filename)

                        # Check if file already exists at destination
                        if os.path.exists(dest_path):
                            errors.append({
                                'file': filename,
                                'error': f'File already exists at destination'
                            })
                            continue

                        # Move the file
                        shutil.move(source_path, dest_path)

                        # Get file info
                        stat = os.stat(dest_path)
                        moved_files.append({
                            'name': filename,
                            'source': source_path,
                            'destination': dest_path,
                            'size': stat.st_size,
                            'readable_size': FileOperations._format_size(stat.st_size)
                        })
                    except Exception as e:
                        errors.append({
                            'file': os.path.basename(source_path),
                            'error': str(e)
                        })

            result = {
                'success': True,
                'message': f'Moved {len(moved_files)} file(s) from {source_directory} to {destination_directory}',
                'moved_count': len(moved_files),
                'files': moved_files,
                'source_directory': source_directory,
                'destination_directory': destination_directory,
                'pattern': pattern
            }

            if errors:
                result['errors'] = errors
                result['error_count'] = len(errors)

            return result

        except Exception as e:
            raise Exception(f"Error moving files: {str(e)}")

    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"


class AgentProcessor:
    """
    Process natural language queries using LLM with function calling.

    Uses Ollama's llama3.1:8b model with function calling to intelligently
    determine which file operation to execute based on user queries.
    """

    # Define available tools for LLM function calling
    TOOLS = [
        {
            'type': 'function',
            'function': {
                'name': 'find_files_by_extension',
                'description': 'Find and list files with a specific extension in a directory tree. Use this when the user asks to find, search, or locate files of a certain type.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'directory': {
                            'type': 'string',
                            'description': 'The directory path to search in. Use the user home directory if not specified.'
                        },
                        'extension': {
                            'type': 'string',
                            'description': 'The file extension to search for (e.g., .py, .txt, .js). Include the dot.'
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Maximum number of files to return. Default is 50.',
                            'default': 50
                        }
                    },
                    'required': ['extension']
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'get_largest_files',
                'description': 'Find the largest files in a directory tree. Use this when the user asks about big files, disk space, or which files take up the most space.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'directory': {
                            'type': 'string',
                            'description': 'The directory path to search in. Use the user home directory if not specified.'
                        },
                        'limit': {
                            'type': 'integer',
                            'description': 'Number of largest files to return. Default is 10.',
                            'default': 10
                        }
                    },
                    'required': []
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'create_folder',
                'description': 'Create a new folder/directory. Use this when the user wants to make, create, or add a new folder.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'directory': {
                            'type': 'string',
                            'description': 'The parent directory path where the folder should be created.'
                        },
                        'folder_name': {
                            'type': 'string',
                            'description': 'The name of the new folder to create.'
                        }
                    },
                    'required': ['folder_name']
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'list_directory',
                'description': 'List the contents of a directory, showing files and subdirectories. Use this when the user wants to see what is in a folder or list directory contents.',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'directory': {
                            'type': 'string',
                            'description': 'The directory path to list. Use the user home directory if not specified.'
                        }
                    },
                    'required': []
                }
            }
        },
        {
            'type': 'function',
            'function': {
                'name': 'move_files',
                'description': 'Move files matching a pattern from one directory to another. Use this when the user wants to move, relocate, or organize files by pattern (like Screenshot*.png, *.txt, etc.).',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'source_directory': {
                            'type': 'string',
                            'description': 'The source directory containing files to move.'
                        },
                        'destination_directory': {
                            'type': 'string',
                            'description': 'The destination directory where files should be moved to.'
                        },
                        'pattern': {
                            'type': 'string',
                            'description': 'The file pattern to match (e.g., "Screenshot*.png", "*.txt", "report_*.pdf"). Uses glob pattern syntax.'
                        }
                    },
                    'required': ['source_directory', 'destination_directory', 'pattern']
                }
            }
        }
    ]

    @staticmethod
    def process_query(query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user query using LLM with function calling.

        Args:
            query: Natural language query from user
            context: Optional context (current directory, etc.)

        Returns:
            Dictionary with action type and parameters
        """
        # Default context
        if context is None:
            context = {'directory': BASE_PATH}

        try:
            # Create system message with context
            system_message = f"""You are a helpful file system assistant.
The user's current directory is: {context.get('directory', BASE_PATH)}
When a directory is not specified by the user, use this current directory.
Always use function calling to respond to file operation requests.
Be helpful and interpret user requests intelligently."""

            # Call Ollama with function calling
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[
                    {'role': 'system', 'content': system_message},
                    {'role': 'user', 'content': query}
                ],
                tools=AgentProcessor.TOOLS
            )

            # Check if the model wants to call a function
            if response.get('message', {}).get('tool_calls'):
                tool_call = response['message']['tool_calls'][0]
                function_name = tool_call['function']['name']
                function_args = tool_call['function']['arguments']

                # Map function names to actions and ensure directory is set
                action_map = {
                    'find_files_by_extension': 'find_by_extension',
                    'get_largest_files': 'largest_files',
                    'create_folder': 'create_folder',
                    'list_directory': 'list_directory',
                    'move_files': 'move_files'
                }

                action = action_map.get(function_name)
                if not action:
                    raise Exception(f"Unknown function: {function_name}")

                # Ensure directory is set if not provided
                if 'directory' not in function_args or not function_args['directory']:
                    function_args['directory'] = context.get('directory', BASE_PATH)

                return {
                    'action': action,
                    'params': function_args
                }

            # If no function call, return help message
            return {
                'action': 'help',
                'params': {},
                'llm_response': response.get('message', {}).get('content', 'I can help you with file operations!')
            }

        except Exception as e:
            print(f"Error in LLM processing: {str(e)}")
            # Fallback to help
            return {
                'action': 'help',
                'params': {},
                'error': str(e)
            }


# ============ API ENDPOINTS ============

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint for natural language queries.

    Request body:
        {
            "message": "user query",
            "context": {"directory": "/path"}  # optional
        }

    Returns:
        {
            "response": "agent response",
            "data": { ... },  # results if any
            "action": "action_taken"
        }
    """
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing message in request body'
            }), 400

        message = data['message']
        context = data.get('context', {'directory': BASE_PATH})

        # Process the query
        action_info = AgentProcessor.process_query(message, context)

        # Execute the action
        if action_info['action'] == 'help':
            # Use LLM response if available, otherwise use default
            help_text = action_info.get('llm_response',
                "I can help you with file operations! Try asking me to:\n• Find files by extension (e.g., 'find all .py files')\n• Get largest files (e.g., 'show me the largest files')\n• Create a folder (e.g., 'create folder my_project')\n• List directory contents (e.g., 'list current directory')")

            return jsonify({
                'response': help_text,
                'action': 'help',
                'error': action_info.get('error')
            })

        # This will be handled by /api/execute
        return jsonify({
            'response': f"I'll execute: {action_info['action']}",
            'action_info': action_info
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/execute', methods=['POST'])
def execute():
    """
    Execute a specific file operation.

    Request body:
        {
            "action": "find_by_extension",
            "params": { ... }
        }

    Returns:
        {
            "success": true,
            "data": { ... },
            "message": "operation result"
        }
    """
    try:
        data = request.get_json()

        if not data or 'action' not in data:
            return jsonify({
                'error': 'Missing action in request body'
            }), 400

        action = data['action']
        params = data.get('params', {})

        # Execute the appropriate operation
        if action == 'find_by_extension':
            # Convert limit to int if it's a string (from LLM)
            limit = params.get('limit', 50)
            limit = int(limit) if isinstance(limit, str) else limit

            result = FileOperations.find_files_by_extension(
                params.get('directory', BASE_PATH),
                params.get('extension', '.txt'),
                limit
            )
            return jsonify({
                'success': True,
                'data': result,
                'message': f"Found {len(result)} files"
            })

        elif action == 'largest_files':
            # Convert limit to int if it's a string (from LLM)
            limit = params.get('limit', 10)
            limit = int(limit) if isinstance(limit, str) else limit

            result = FileOperations.get_largest_files(
                params.get('directory', BASE_PATH),
                limit
            )
            return jsonify({
                'success': True,
                'data': result,
                'message': f"Found {len(result)} largest files"
            })

        elif action == 'create_folder':
            result = FileOperations.create_folder(
                params.get('directory', BASE_PATH),
                params.get('folder_name', 'new_folder')
            )
            return jsonify({
                'success': result['success'],
                'data': result,
                'message': result['message']
            })

        elif action == 'list_directory':
            result = FileOperations.list_directory(
                params.get('directory', BASE_PATH)
            )
            return jsonify({
                'success': True,
                'data': result,
                'message': f"Listed {len(result['items'])} items"
            })

        elif action == 'move_files':
            result = FileOperations.move_files(
                params.get('source_directory'),
                params.get('destination_directory'),
                params.get('pattern')
            )
            return jsonify({
                'success': result['success'],
                'data': result,
                'message': result['message']
            })

        else:
            return jsonify({
                'error': f'Unknown action: {action}'
            }), 400

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'base_path': BASE_PATH
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API information."""
    return jsonify({
        'name': 'Local File Manager Agent API',
        'version': '1.0.0',
        'endpoints': {
            '/api/chat': 'POST - Natural language chat interface',
            '/api/execute': 'POST - Execute file operations',
            '/api/health': 'GET - Health check'
        }
    })


if __name__ == '__main__':
    print("🚀 Starting Local File Manager Agent...")
    print(f"📁 Base path: {BASE_PATH}")
    print(f"🤖 AI Model: {OLLAMA_MODEL} (with function calling)")
    print("🌐 Server running on http://localhost:5001")
    print("\n✨ LLM-powered intelligent file operations enabled!")
    app.run(debug=True, host='0.0.0.0', port=5001)
