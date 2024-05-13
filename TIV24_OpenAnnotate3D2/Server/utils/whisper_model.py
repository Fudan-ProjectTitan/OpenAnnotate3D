import whisper

whisper_model = whisper.load_model("base")
def speech_recognition(speech_file):
        # whisper
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(speech_file)
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(whisper_model.device)

        # detect the spoken language
        _, probs = whisper_model.detect_language(mel)
        speech_language = max(probs, key=probs.get)

        # decode the audio
        options = whisper.DecodingOptions(
            temperature=0.8,
            length_penalty=0.9,
        )
        result = whisper.decode(whisper_model, mel, options)
        speech_text = result.text
        return speech_text, speech_language