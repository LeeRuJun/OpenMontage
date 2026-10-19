import sys
from types import SimpleNamespace


def test_minimax_tts_writes_audio_from_hex_response(tmp_path, monkeypatch):
    from tools.audio.minimax_tts import MiniMaxTTS

    calls = []

    class FakeResponse:
        status_code = 200
        text = ""

        def json(self):
            return {
                "data": {"audio": "000102ff", "status": 2},
                "extra_info": {
                    "audio_length": 1234,
                    "usage_characters": 20,
                    "audio_format": "mp3",
                    "audio_sample_rate": 32000,
                    "audio_channel": 1,
                },
                "trace_id": "trace-123",
                "base_resp": {"status_code": 0, "status_msg": "success"},
            }

    def fake_post(url, *, params, headers, json, timeout):
        calls.append({
            "url": url,
            "params": params,
            "headers": headers,
            "json": json,
            "timeout": timeout,
        })
        return FakeResponse()

    monkeypatch.setenv("MINIMAX_TTS_API_KEY", "test-key")
    monkeypatch.setenv("MINIMAX_GROUP_ID", "group-1")
    monkeypatch.setitem(sys.modules, "requests", SimpleNamespace(post=fake_post))
    monkeypatch.setattr(MiniMaxTTS, "_audio_duration", staticmethod(lambda path: 1.23))

    out = tmp_path / "sample.mp3"
    result = MiniMaxTTS().execute({
        "text": "测试讲书人声音。",
        "voice_id": "Chinese (Mandarin)_Gentle_Senior",
        "model": "speech-2.8-hd",
        "speed": 1.0,
        "emotion": "calm",
        "output_path": str(out),
    })

    assert result.success, result.error
    assert out.read_bytes() == b"\x00\x01\x02\xff"
    assert calls[0]["url"] == "https://api-uw.minimax.io/v1/t2a_v2"
    assert calls[0]["params"] == {"GroupId": "group-1"}
    assert calls[0]["headers"]["Authorization"] == "Bearer test-key"
    assert calls[0]["json"]["model"] == "speech-2.8-hd"
    assert calls[0]["json"]["voice_setting"] == {
        "voice_id": "Chinese (Mandarin)_Gentle_Senior",
        "speed": 1.0,
        "vol": 1,
        "pitch": 0,
        "emotion": "calm",
    }
    assert type(calls[0]["json"]["voice_setting"]["vol"]) is int
    assert type(calls[0]["json"]["voice_setting"]["pitch"]) is int
    assert calls[0]["json"]["audio_setting"]["format"] == "mp3"
    assert result.data["audio_duration_seconds"] == 1.23
    assert result.data["usage_characters"] == 20


def test_minimax_tts_requires_key_and_group(monkeypatch):
    from tools.audio.minimax_tts import MiniMaxTTS

    monkeypatch.delenv("MINIMAX_TTS_API_KEY", raising=False)
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    monkeypatch.delenv("MINIMAX_GROUP_ID", raising=False)
    monkeypatch.delenv("MINIMAX_GROUPID", raising=False)

    result = MiniMaxTTS().execute({"text": "测试"})

    assert not result.success
    assert "MINIMAX_TTS_API_KEY" in result.error
