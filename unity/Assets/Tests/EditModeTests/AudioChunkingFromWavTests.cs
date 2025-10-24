using NUnit.Framework;
using UnityEngine;
#if UNITY_EDITOR
using UnityEditor;
#endif
using System;
using System.Reflection;

public class AudioChunkingFromWavTests
{
#if UNITY_EDITOR
    private const string TestWavPath = "Assets/Audio/test.wav";

    private MethodInfo GetPrivateMethod(Type type, string name)
    {
        return type.GetMethod(name, BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static);
    }

    [Test]
    public void CanLoad_TestWav_AudioClip()
    {
        var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(TestWavPath);
        Assert.IsNotNull(clip, $"Failed to load AudioClip at {TestWavPath}");
        Assert.Greater(clip.samples, 0, "Clip has no samples");
    }

    [Test]
    public void ReadSamplesWrap_ProducesContiguousDataAcrossWrap()
    {
        var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(TestWavPath);
        Assert.IsNotNull(clip);

        // Create component to access private ReadSamplesWrap via reflection
        var go = new GameObject("AudioMgrTest");
        var mgr = go.AddComponent<AudioRecordingManager>();

        int channels = clip.channels;
        int totalSamplesToRead = Mathf.Max(1, clip.samples / 2); // read half the clip
        int start = Mathf.Max(0, clip.samples - (clip.samples / 4)); // start at 3/4 so we wrap by 1/4

        var method = GetPrivateMethod(typeof(AudioRecordingManager), "ReadSamplesWrap");
        Assert.IsNotNull(method, "ReadSamplesWrap not found via reflection");

        object[] args = new object[] { clip, start, totalSamplesToRead };
        var wrapped = (float[])method.Invoke(mgr, args);
        Assert.AreEqual(totalSamplesToRead * channels, wrapped.Length);

        // Build expected data by stitching end segment + beginning segment
        int firstLen = Mathf.Min(totalSamplesToRead, clip.samples - start);
        int tailLen = totalSamplesToRead - firstLen;

        float[] endSeg = new float[firstLen * channels];
        clip.GetData(endSeg, start);

        float[] beginSeg = new float[tailLen * channels];
        if (tailLen > 0) clip.GetData(beginSeg, 0);

        // Compare content with small tolerance
        int idx = 0;
        for (int i = 0; i < endSeg.Length; i++, idx++)
        {
            Assert.AreEqual(endSeg[i], wrapped[idx], 1e-5f, $"Mismatch in end segment at {i}");
        }
        for (int i = 0; i < beginSeg.Length; i++, idx++)
        {
            Assert.AreEqual(beginSeg[i], wrapped[idx], 1e-5f, $"Mismatch in begin segment at {i}");
        }

        GameObject.DestroyImmediate(go);
    }

    [Test]
    public void HasSufficientVolume_ReturnsTrue_On_TestWav()
    {
        var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(TestWavPath);
        Assert.IsNotNull(clip);

        // Ensure audio data is actually loaded before GetData
        if (!clip.preloadAudioData)
        {
            clip.LoadAudioData();
        }

        // Wait (briefly) until data is loaded
        var startTime = DateTime.Now;
        while (clip.loadState == AudioDataLoadState.Loading && (DateTime.Now - startTime).TotalSeconds < 5)
        {
            // spin a bit
        }
        Assert.AreNotEqual(AudioDataLoadState.Failed, clip.loadState, "Audio data failed to load for test.wav");

        var go = new GameObject("AudioMgrTestVol");
        var mgr = go.AddComponent<AudioRecordingManager>();
        // Very conservative threshold; detection function also checks peak twice the threshold
        mgr.silenceThreshold = 0.0005f;

        var method = GetPrivateMethod(typeof(AudioRecordingManager), "HasSufficientVolume");
        Assert.IsNotNull(method, "HasSufficientVolume not found via reflection");

        int channels = clip.channels;
        int window = Mathf.Max(1, clip.frequency / 2); // ~0.5s window
        bool detected = false;
        for (int start = 0; start < clip.samples; start += window)
        {
            int count = Mathf.Min(window, clip.samples - start);
            float[] buf = new float[count * channels];
            bool ok = clip.GetData(buf, start);
            if (!ok) continue; // skip if chunk not available (shouldn't happen once loaded)

            bool hasVol = (bool)method.Invoke(mgr, new object[] { buf });
            if (hasVol)
            {
                detected = true;
                break;
            }
        }

        Assert.IsTrue(detected, "Expected non-silent segment somewhere in test.wav");

        GameObject.DestroyImmediate(go);
    }

    [Test]
    public void ConvertSamplesToWav_ProducesValidWavHeader()
    {
        var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(TestWavPath);
        Assert.IsNotNull(clip);

        int channels = clip.channels;
        int sampleCount = Mathf.Min(clip.samples, clip.frequency / 4); // ~0.25s
        float[] buffer = new float[sampleCount * channels];
        clip.GetData(buffer, 0);

        byte[] wav = AudioRecordingManager.ConvertSamplesToWav(buffer, clip.frequency, channels);
        Assert.Greater(wav.Length, 44, "WAV should have header + data");

        // Check header tags
        Assert.AreEqual((byte)'R', wav[0]);
        Assert.AreEqual((byte)'I', wav[1]);
        Assert.AreEqual((byte)'F', wav[2]);
        Assert.AreEqual((byte)'F', wav[3]);

        Assert.AreEqual((byte)'W', wav[8]);
        Assert.AreEqual((byte)'A', wav[9]);
        Assert.AreEqual((byte)'V', wav[10]);
        Assert.AreEqual((byte)'E', wav[11]);

        Assert.AreEqual((byte)'f', wav[12]); // 'fmt '
        Assert.AreEqual((byte)'m', wav[13]);
        Assert.AreEqual((byte)'t', wav[14]);

        Assert.AreEqual((byte)'d', wav[36]); // 'data'
        Assert.AreEqual((byte)'a', wav[37]);
        Assert.AreEqual((byte)'t', wav[38]);
        Assert.AreEqual((byte)'a', wav[39]);
    }
#endif
}


