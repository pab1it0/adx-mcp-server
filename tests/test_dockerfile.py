#!/usr/bin/env python3
import os
import subprocess
import sys
import unittest
import tempfile
import time
import docker
import requests
from pathlib import Path

class DockerfileTest(unittest.TestCase):
    """Test suite for validating the Dockerfile and container functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up resources needed for testing."""
        cls.client = docker.from_env()
        cls.image_name = "adx-mcp-server-test"
        cls.container_name = "adx-mcp-server-test-container"
        cls.repo_root = Path(__file__).parent.parent.absolute()
        
        # Build the Docker image
        print(f"Building Docker image: {cls.image_name}")
        try:
            # Use subprocess to capture the build output
            build_cmd = [
                "docker", "build", 
                "-t", cls.image_name,
                "-f", str(cls.repo_root / "Dockerfile"),
                str(cls.repo_root)
            ]
            result = subprocess.run(
                build_cmd, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"Build output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to build Docker image: {e}")
            print(f"Error output: {e.stderr}")
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Clean up resources after testing."""
        # Remove the container if it exists
        try:
            container = cls.client.containers.get(cls.container_name)
            container.remove(force=True)
            print(f"Removed container: {cls.container_name}")
        except docker.errors.NotFound:
            pass
        
        # Remove the image
        try:
            cls.client.images.remove(cls.image_name, force=True)
            print(f"Removed image: {cls.image_name}")
        except docker.errors.ImageNotFound:
            pass
    
    def test_image_structure(self):
        """Test that the Docker image has the correct structure."""
        # Inspect the image
        image = self.client.images.get(self.image_name)
        self.assertIsNotNone(image, "Docker image was not created successfully")
        
        # Check image metadata
        inspect_result = self.client.api.inspect_image(self.image_name)
        
        # Check labels
        labels = inspect_result['Config']['Labels']
        self.assertEqual(labels['maintainer'], 'pab1it0', "Maintainer label incorrect")
        self.assertEqual(labels['description'], 'Azure Data Explorer MCP Server', "Description label incorrect")
        
        # Check environment variables
        env_vars = inspect_result['Config']['Env']
        self.assertTrue(any('PYTHONUNBUFFERED=1' in var for var in env_vars), "PYTHONUNBUFFERED env var not set")
        self.assertTrue(any('PATH=/app/.venv/bin:' in var for var in env_vars), "PATH env var not set correctly")
        
        # Check entrypoint
        entrypoint = inspect_result['Config']['Entrypoint']
        self.assertEqual(entrypoint, ['adx-mcp-server'], "Entrypoint is incorrect")
    
    def test_container_startup(self):
        """Test that the container starts up correctly with the right environment variables."""
        # Create temp file to capture logs
        log_file = tempfile.NamedTemporaryFile(delete=False)
        log_file.close()
        
        try:
            # Run a container with minimal environment to test startup
            # Note: We expect it to exit with an error due to missing ADX configuration
            # We just want to verify it starts and runs the entrypoint correctly
            container = self.client.containers.run(
                self.image_name,
                name=self.container_name,
                environment={
                    "ADX_CLUSTER_URL": "https://example.kusto.windows.net",
                    "ADX_DATABASE": "testdb"
                },
                detach=True,
                remove=False
            )
            
            # Wait for container to finish startup (it will exit due to missing auth)
            time.sleep(2)
            
            # Get container logs
            logs = container.logs().decode('utf-8')
            
            # Since we're no longer using the docker-entrypoint.sh script,
            # we need to update our expectations. We expect to see an error about 
            # authentication or connection, but the container should have started
            self.assertTrue(len(logs) > 0, "Container didn't output any logs")
            # We expect to either see connection errors or authentication errors
            connection_error = "Unable to connect" in logs or "Failed to" in logs or "Error" in logs
            self.assertTrue(connection_error, "Container didn't attempt to connect to ADX")
            
            # Check container state
            container.reload()
            # We expect it to exit because we didn't provide all required configuration
            self.assertIn(container.status, ["exited", "dead"], 
                         "Container should have exited due to missing configuration")
            
        finally:
            # Clean up the log file
            os.unlink(log_file.name)


# Allow running this test directly
if __name__ == "__main__":
    unittest.main()
