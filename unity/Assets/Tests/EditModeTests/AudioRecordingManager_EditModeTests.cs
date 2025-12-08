using NUnit.Framework;
using UnityEngine;
using System.Reflection;

/// <summary>
/// Edit mode tests for AudioRecordingManager
/// Tests core functionality of audio recording, chunking, and metadata handling
/// </summary>
public class AudioRecordingManager_EditModeTests
{
    private GameObject testGameObject;
    private AudioRecordingManager manager;

    [SetUp]
    public void SetUp()
    {
        testGameObject = new GameObject("AudioRecordingManagerTest");
        manager = testGameObject.AddComponent<AudioRecordingManager>();
    }

    [TearDown]
    public void TearDown()
    {
        if (testGameObject != null)
        {
            UnityEngine.Object.DestroyImmediate(testGameObject);
        }
    }

    [Test]
    public void AudioRecordingManager_InitializesWithDefaultValues()
    {
        // Assert default values are set correctly
        Assert.AreEqual(8f, manager.chunkDurationSeconds, "Default chunk duration should be 8 seconds");
        Assert.AreEqual(48000, manager.targetSampleRate, "Default sample rate should be 48000 Hz");
        Assert.AreEqual(0.01f, manager.silenceThreshold, "Default silence threshold should be 0.01");
        Assert.AreEqual(0.5f, manager.chunkOverlapSeconds, "Default overlap should be 0.5 seconds");
    }

    [Test]
    public void ConvertSamplesToWav_CreatesValidWavHeader()
    {
        // Arrange
        float[] samples = new float[1000];
        for (int i = 0; i < samples.Length; i++)
        {
            samples[i] = Mathf.Sin(i * 0.1f); // Create simple sine wave
        }
        int sampleRate = 44100;
        int channels = 1;

        // Act
        byte[] wavData = AudioRecordingManager.ConvertSamplesToWav(samples, sampleRate, channels);

        // Assert - Check header structure
        Assert.Greater(wavData.Length, 44, "WAV file should have header + data");
        
        // Check RIFF header
        Assert.AreEqual((byte)'R', wavData[0]);
        Assert.AreEqual((byte)'I', wavData[1]);
        Assert.AreEqual((byte)'F', wavData[2]);
        Assert.AreEqual((byte)'F', wavData[3]);
        
        // Check WAVE format
        Assert.AreEqual((byte)'W', wavData[8]);
        Assert.AreEqual((byte)'A', wavData[9]);
        Assert.AreEqual((byte)'V', wavData[10]);
        Assert.AreEqual((byte)'E', wavData[11]);
        
        // Check fmt chunk
        Assert.AreEqual((byte)'f', wavData[12]);
        Assert.AreEqual((byte)'m', wavData[13]);
        Assert.AreEqual((byte)'t', wavData[14]);
        Assert.AreEqual((byte)' ', wavData[15]);
        
        // Check data chunk
        Assert.AreEqual((byte)'d', wavData[36]);
        Assert.AreEqual((byte)'a', wavData[37]);
        Assert.AreEqual((byte)'t', wavData[38]);
        Assert.AreEqual((byte)'a', wavData[39]);
    }

    [Test]
    public void ConvertSamplesToWav_CorrectDataSize()
    {
        // Arrange
        float[] samples = new float[1000];
        int sampleRate = 44100;
        int channels = 2;

        // Act
        byte[] wavData = AudioRecordingManager.ConvertSamplesToWav(samples, sampleRate, channels);

        // Assert - Each sample becomes 2 bytes (16-bit PCM), plus 44-byte header
        int expectedSize = 44 + (samples.Length * 2);
        Assert.AreEqual(expectedSize, wavData.Length, "WAV data size should be header + samples * 2 bytes");
    }

    [Test]
    public void ConvertSamplesToWav_HandlesStereo()
    {
        // Arrange
        float[] samples = new float[500];
        int sampleRate = 48000;
        int channels = 2;

        // Act
        byte[] wavData = AudioRecordingManager.ConvertSamplesToWav(samples, sampleRate, channels);

        // Assert - Check channel count in header (offset 22, 2 bytes)
        ushort channelCount = System.BitConverter.ToUInt16(wavData, 22);
        Assert.AreEqual(channels, channelCount, "Channel count should be stored correctly");
    }

    [Test]
    public void ConvertSamplesToWav_ClampsSampleValues()
    {
        // Arrange - Create samples outside [-1, 1] range
        float[] samples = new float[] { -2.0f, 2.0f, 0.5f, -0.5f };
        int sampleRate = 44100;
        int channels = 1;

        // Act
        byte[] wavData = AudioRecordingManager.ConvertSamplesToWav(samples, sampleRate, channels);

        // Assert - Should not throw and should create valid WAV
        Assert.Greater(wavData.Length, 44);
        
        // Extract first sample (after 44-byte header)
        short firstSample = System.BitConverter.ToInt16(wavData, 44);
        short secondSample = System.BitConverter.ToInt16(wavData, 46);
        
        // Should be clamped near short.MaxValue and short.MinValue
        // Allow for rounding: -32768 or -32767 are both acceptable
        Assert.GreaterOrEqual(firstSample, short.MinValue, "Sample should be >= minimum short value");
        Assert.LessOrEqual(firstSample, short.MinValue + 1, "Sample should be clamped near minimum (within 1)");
        Assert.AreEqual(short.MaxValue, secondSample, "Sample should be clamped to maximum");
    }

    [Test]
    public void HasSufficientVolume_DetectsSilence()
    {
        // Arrange
        float[] silentSamples = new float[1000];
        // All zeros = silence
        
        var method = GetPrivateMethod("HasSufficientVolume");

        // Act
        bool result = (bool)method.Invoke(manager, new object[] { silentSamples });

        // Assert
        Assert.IsFalse(result, "Silent samples should not have sufficient volume");
    }

    [Test]
    public void HasSufficientVolume_DetectsSound()
    {
        // Arrange
        float[] samples = new float[1000];
        for (int i = 0; i < samples.Length; i++)
        {
            samples[i] = Mathf.Sin(i * 0.1f) * 0.5f; // Audible sine wave
        }
        
        var method = GetPrivateMethod("HasSufficientVolume");

        // Act
        bool result = (bool)method.Invoke(manager, new object[] { samples });

        // Assert
        Assert.IsTrue(result, "Audible samples should have sufficient volume");
    }

    [Test]
    public void HasSufficientVolume_RespectsThreshold()
    {
        // Arrange
        manager.silenceThreshold = 0.1f; // Higher threshold
        float[] quietSamples = new float[1000];
        for (int i = 0; i < quietSamples.Length; i++)
        {
            quietSamples[i] = 0.01f; // Below threshold
        }
        
        var method = GetPrivateMethod("HasSufficientVolume");

        // Act
        bool result = (bool)method.Invoke(manager, new object[] { quietSamples });

        // Assert
        Assert.IsFalse(result, "Samples below threshold should not have sufficient volume");
    }

    [Test]
    public void OverlapSamples_CalculatedCorrectly()
    {
        // Arrange
        manager.chunkOverlapSeconds = 1.0f;
        manager.targetSampleRate = 48000;
        
        // Call Start to calculate overlapSamples
        var startMethod = GetPrivateMethod("Start");
        startMethod.Invoke(manager, null);
        
        // Get the private overlapSamples field
        var overlapField = typeof(AudioRecordingManager).GetField("overlapSamples", 
            BindingFlags.NonPublic | BindingFlags.Instance);
        int overlapSamples = (int)overlapField.GetValue(manager);

        // Assert
        Assert.AreEqual(48000, overlapSamples, "Overlap samples should be sampleRate * overlapSeconds");
    }

    [Test]
    public void ConvertSamplesToWav_EmptySamples_CreatesMinimalWav()
    {
        // Arrange
        float[] samples = new float[0];
        int sampleRate = 44100;
        int channels = 1;

        // Act
        byte[] wavData = AudioRecordingManager.ConvertSamplesToWav(samples, sampleRate, channels);

        // Assert - Should still have valid header
        Assert.AreEqual(44, wavData.Length, "Empty samples should still create valid WAV header");
    }

    private MethodInfo GetPrivateMethod(string methodName)
    {
        return typeof(AudioRecordingManager).GetMethod(methodName, 
            BindingFlags.NonPublic | BindingFlags.Instance);
    }
}