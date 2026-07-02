import React, { useState, useCallback, useRef } from 'react';
import './App.css';

function App() {
    const [files, setFiles] = useState([]);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef(null);

    // Форматирование размера файла в удобный вид
    const formatFileSize = (bytes) => {
        if (bytes === 0) return '0 Б';
        const k = 1024;
        const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
    };

    // Обработка выбранных файлов (из input или drag-drop)
    const handleFiles = useCallback((fileList) => {
        const newFiles = Array.from(fileList).filter(
            (file) =>
                file.type === 'application/pdf' ||
                file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        );
        if (newFiles.length > 0) {
            setFiles((prev) => [...prev, ...newFiles]);
        } else {
            alert('Пожалуйста, выберите файлы WORD или PDF.');
        }
    }, []);

    // Обработчик изменения input
    const handleInputChange = (e) => {
        if (e.target.files) {
            handleFiles(e.target.files);
        }
        e.target.value = ''; // сброс, чтобы можно было выбрать те же файлы повторно
    };

    // Обработчики drag-and-drop
    const handleDragEnter = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDragOver = (e) => {
        e.preventDefault(); // обязательно для разрешения drop
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files) {
            handleFiles(e.dataTransfer.files);
        }
    };

    // Обработчик поиска (заглушка)
    const handleSearch = () => {
        if (files.length === 0) return;
        alert(`Поиск ${files.length} в файлах`);
        
    };

    // Удаление файла из списка
    const removeFile = (indexToRemove) => {
        setFiles((prev) => prev.filter((_, index) => index !== indexToRemove));
    };

    return (
        <div className="search-card">
            <h1>Найти в ваших документах</h1>
            <p className="subtitle">
                Анализ ваших документов.
            </p>

            <div
                className={`drop-zone ${isDragging ? 'dragover' : ''}`}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    accept=".doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    multiple
                    onChange={handleInputChange}
                    ref={fileInputRef}
                />
                <p> Перетащите файлы сюда</p>
                <div className="or-text">или</div>
                <span className="browse-btn">Выбрать файлы</span>
            </div>

            {files.length > 0 && (
                <>
                    <div className="file-list">
                        {files.map((file, index) => (
                            <div key={index} className="file-item">
                                <span className="file-name">{file.name}</span>
                                <span className="file-size">{formatFileSize(file.size)}</span>
                                <button
                                    onClick={() => removeFile(index)}
                                    style={{
                                        background: 'none',
                                        border: 'none',
                                        color: '#e74c3c',
                                        fontSize: '1.2rem',
                                        cursor: 'pointer',
                                        padding: '0 8px',
                                    }}
                                    aria-label="Удалить файл"
                                >
                                    ✕
                                </button>
                            </div>
                        ))}
                    </div>
                    <button className="convert-btn" onClick={handleConvert}>
                        Анализ {files.length} файл(ов)
                    </button>
                </>
            )}
        </div>
    );
}

export default App;