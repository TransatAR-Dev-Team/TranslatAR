"""
Integration tests for audio processing and translation endpoints.
Tests cover audio upload, STT processing, translation, and database persistence.
"""
import pytest
import httpx
import io
from datetime import datetime

BACKEND_URL = "http://backend:8000/api"


@pytest.fixture
async def auth_token():
    """Fixture to provide a valid authentication token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BACKEND_URL}/test-auth/get-token")
        return response.json()["access_token"]


def create_dummy_audio_file(duration_ms: int = 1000):
    """Create a dummy WAV file for testing."""
    # Simple WAV file header for mono 16-bit PCM at 44100 Hz
    sample_rate = 44100
    num_samples = int(sample_rate * duration_ms / 1000)
    
    # WAV header
    wav_header = bytearray([
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x00, 0x00, 0x00, 0x00,  # File size (placeholder)
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        0x66, 0x6D, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # fmt chunk size (16)
        0x01, 0x00,              # Audio format (1 = PCM)
        0x01, 0x00,              # Number of channels (1 = mono)
        0x44, 0xAC, 0x00, 0x00,  # Sample rate (44100)
        0x88, 0x58, 0x01, 0x00,  # Byte rate
        0x02, 0x00,              # Block align
        0x10, 0x00,              # Bits per sample (16)
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x00, 0x00, 0x00, 0x00,  # Data chunk size (placeholder)
    ])
    
    # Create dummy audio data (silence)
    audio_data = bytes(num_samples * 2)  # 2 bytes per sample for 16-bit
    
    # Update file size in header
    file_size = len(wav_header) + len(audio_data) - 8
    wav_header[4:8] = file_size.to_bytes(4, byteorder='little')
    
    # Update data chunk size
    data_size = len(audio_data)
    wav_header[40:44] = data_size.to_bytes(4, byteorder='little')
    
    return io.BytesIO(wav_header + audio_data)


@pytest.mark.asyncio
async def test_process_audio_en_to_es(auth_token):
    """Test audio processing with English to Spanish translation."""
    audio_file = create_dummy_audio_file()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        files = {"audio_file": ("test.wav", audio_file, "audio/wav")}
        data = {
            "source_lang": "en",
            "target_lang": "es"
        }
        
        response = await client.post(
            f"{BACKEND_URL}/process-audio",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Mock services return "hello world" and "[es] hello world"
        assert "original_text" in result
        assert "translated_text" in result
        assert result["original_text"] == "hello world"
        assert result["translated_text"] == "[es] hello world"


@pytest.mark.asyncio
async def test_process_audio_different_languages(auth_token):
    """Test audio processing with different language pairs."""
    language_pairs = [
        ("en", "fr"),
        ("en", "de"),
        ("es", "en"),
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        for source, target in language_pairs:
            audio_file = create_dummy_audio_file()
            files = {"audio_file": ("test.wav", audio_file, "audio/wav")}
            data = {
                "source_lang": source,
                "target_lang": target
            }
            
            response = await client.post(
                f"{BACKEND_URL}/process-audio",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["translated_text"] == f"[{target}] hello world"


@pytest.mark.asyncio
async def test_process_audio_without_auth():
    """Test that audio processing requires authentication."""
    audio_file = create_dummy_audio_file()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        files = {"audio_file": ("test.wav", audio_file, "audio/wav")}
        data = {
            "source_lang": "en",
            "target_lang": "es"
        }
        
        response = await client.post(
            f"{BACKEND_URL}/process-audio",
            files=files,
            data=data
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_process_audio_saves_to_database(auth_token):
    """Test that processed audio is saved to translation history."""
    audio_file = create_dummy_audio_file()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Process audio
        files = {"audio_file": ("test.wav", audio_file, "audio/wav")}
        data = {
            "source_lang": "en",
            "target_lang": "es"
        }
        
        await client.post(
            f"{BACKEND_URL}/process-audio",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Check history
        history_response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert history_response.status_code == 200
        history = history_response.json()["history"]
        
        # Should have at least one entry
        assert len(history) > 0
        
        # Most recent entry should match our translation
        latest = history[0]
        assert latest["original_text"] == "hello world"
        assert latest["translated_text"] == "[es] hello world"


@pytest.mark.asyncio
async def test_process_audio_invalid_file(auth_token):
    """Test processing with invalid audio file."""
    # Create invalid file (just random bytes)
    invalid_file = io.BytesIO(b"This is not a valid audio file")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        files = {"audio_file": ("test.wav", invalid_file, "audio/wav")}
        data = {
            "source_lang": "en",
            "target_lang": "es"
        }
        
        response = await client.post(
            f"{BACKEND_URL}/process-audio",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should still return 200 with mock services
        # In real implementation, might return different status
        assert response.status_code in [200, 400, 502]


@pytest.mark.asyncio
async def test_process_audio_large_file(auth_token):
    """Test processing with larger audio file."""
    # Create a 10-second audio file
    large_audio_file = create_dummy_audio_file(duration_ms=10000)
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        files = {"audio_file": ("large_test.wav", large_audio_file, "audio/wav")}
        data = {
            "source_lang": "en",
            "target_lang": "es"
        }
        
        response = await client.post(
            f"{BACKEND_URL}/process-audio",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_process_audio_concurrent_requests(auth_token):
    """Test processing multiple audio files concurrently."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        tasks = []
        
        for i in range(3):
            audio_file = create_dummy_audio_file()
            files = {"audio_file": (f"test{i}.wav", audio_file, "audio/wav")}
            data = {
                "source_lang": "en",
                "target_lang": "es"
            }
            
            task = client.post(
                f"{BACKEND_URL}/process-audio",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for response in responses:
            assert not isinstance(response, Exception)
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_process_audio_missing_parameters(auth_token):
    """Test that missing required parameters are handled."""
    audio_file = create_dummy_audio_file()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Missing target_lang
        files = {"audio_file": ("test.wav", audio_file, "audio/wav")}
        data = {"source_lang": "en"}
        
        response = await client.post(
            f"{BACKEND_URL}/process-audio",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should use defaults or return 422
        assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_process_audio_metadata_in_database(auth_token):
    """Test that language metadata is correctly stored."""
    audio_file = create_dummy_audio_file()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        files = {"audio_file": ("test.wav", audio_file, "audio/wav")}
        data = {
            "source_lang": "fr",
            "target_lang": "de"
        }
        
        await client.post(
            f"{BACKEND_URL}/process-audio",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Retrieve and verify metadata
        history_response = await client.get(
            f"{BACKEND_URL}/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        history = history_response.json()["history"]
        latest = history[0]
        
        # Check language detection metadata
        assert "detected_language" in latest
        assert "language_probability" in latest


import asyncio
