import React, { useState } from 'react';
import {
    FileUploaderButton,
    Button,
    InlineLoading,
} from '@carbon/react';
import { Upload } from '@carbon/icons-react';
import ReactMarkdown from 'react-markdown';

const AudioSummarizer = () => {
    const [file, setFile] = useState(null);
    const [markdown, setMarkdown] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async () => {
        if (!file) {
            setError('Please upload an audio file.');
            return;
        }

        setLoading(true);
        setError('');
        setMarkdown('');

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('http://127.0.0.1:8000/api/audio/summary', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Failed to get summary');

            const data = await response.json();
            setMarkdown(data.summary || '');
        } catch (err) {
            console.error(err);
            setError('Error occurred while summarizing audio.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '700px', margin: '2rem auto' }}>
            <h2>Audio Summarizer</h2>

            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1.5rem' }}>
                <FileUploaderButton
                    size="md"
                    labelText={
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <Upload size={16} />
                            Upload Audio
                        </span>
                    }
                    accept={['.mp3', '.wav']}
                    multiple={false}
                    onChange={(event) => {
                        const selectedFile = event.target?.files?.[0];
                        setFile(selectedFile);
                        setMarkdown('');
                        setError('');
                    }}
                />

                <Button
                    kind="primary"
                    size="md"
                    onClick={handleSubmit}
                    disabled={loading}
                >
                    {loading ? <InlineLoading description="Submitting..." /> : 'Submit'}
                </Button>
            </div>


            {error && <div style={{ marginTop: '1rem', color: 'red' }}>{error}</div>}

            {markdown && (
                <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '5px' }}>
                    <h4>Summary:</h4>
                    <ReactMarkdown>{markdown}</ReactMarkdown>
                </div>
            )}
        </div>
    );
};

export default AudioSummarizer;
