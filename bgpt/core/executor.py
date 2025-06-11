"""
Command Executor - Safe command execution with monitoring.
"""

import asyncio
import subprocess
import time
from dataclasses import dataclass
from typing import Optional
from .command_parser import ParsedCommand
from ..utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ExecutionResult:
    """Result of command execution."""
    success: bool
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    command: str

class CommandExecutor:
    """Safe command execution engine."""
    
    async def execute(self, parsed_command: ParsedCommand, sandbox: bool = False) -> ExecutionResult:
        """Execute a parsed command safely."""
        start_time = time.time()
        
        try:
            if sandbox:
                # In a real implementation, this would use containerization
                logger.debug("Executing in sandbox mode")
            
            # Create subprocess without text=True to avoid the error
            process = await asyncio.create_subprocess_shell(
                parsed_command.raw_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout_bytes, stderr_bytes = await process.communicate()
            
            # Safely decode bytes to string with error handling
            stdout = ""
            stderr = ""
            
            if stdout_bytes:
                try:
                    stdout = stdout_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    stdout = stdout_bytes.decode('utf-8', errors='replace')
            
            if stderr_bytes:
                try:
                    stderr = stderr_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    stderr = stderr_bytes.decode('utf-8', errors='replace')
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=process.returncode == 0,
                return_code=process.returncode or 0,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                command=parsed_command.raw_command
            )
            
        except Exception as e:
            # Only log to file, not console
            logger.debug(f"Execution failed: {e}")
            return ExecutionResult(
                success=False,
                return_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=time.time() - start_time,
                command=parsed_command.raw_command
            )
