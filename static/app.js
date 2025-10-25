const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const dropText = document.getElementById('dropText');
const fileSelected = document.getElementById('fileSelected');
const fileName = document.getElementById('fileName');
const changeFileBtn = document.getElementById('changeFile');

dropzone.addEventListener('click', (e) => {
    if (!e.target.closest('#changeFile')) {
        fileInput.click();
    }
})

fileInput.addEventListener('change', handleFileSelect);
changeFileBtn.addEventListener('click', () => fileInput.click())

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`
        dropText.classList.add('hidden');
        fileSelected.classList.remove('hidden');
    }
}

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('border-secondary', 'bg-base-200');
})

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('border-secondary', 'bg-base-200')
})

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('border-secondary', 'bg-base-200')

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect({ target: { files } })
    }
})

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!fileInput.files.length) {
        alert('Please select a file first.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    loading.classList.remove('hidden');
    results.classList.add('hidden')

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        })

        const data = await response.json();

        if (response.ok) {
            displayResults(data);
        } else {
            alert('Error: ' + (data.error || 'Analysis failed'));
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        loading.classList.add('hidden');
    }
})

function displayResults(data) {
    document.getElementById('resFilename').textContent = data.filename;
    document.getElementById('resFileType').textContent = data.file_type;
    document.getElementById('resExtension').textContent = data.file_extension;

    const analysisContainer = document.getElementById('analysisResults');
    analysisContainer.innerHTML = '';

    data.analyses.forEach(analysis => {
        const section = createAnalysisSection(analysis, data.analysis_id);
        analysisContainer.appendChild(section);
    });

    if (data.filters && Object.keys(data.filters).length > 0) {
        displayFilters(data.filters, data.analysis_id);
    }

    results.classList.remove('hidden');
    results.scrollIntoView({ behavior: 'smooth' });
}

function createAnalysisSection(analysis, analysisId) {
    const section = document.createElement('section');
    section.className = 'card bg-base-100 shadow-xl';

    const badge = analysis.success
        ? '<div class="badge badge-success">Success</div>'
        : '<div class="badge badge-error">Failed</div>';

    let content = `
        <div class="card-body">
            <div class="flex justify-between items-center mb-4">
                <h2 class="card-title">${analysis.tool}</h2>
                ${badge}
            </div>
    `;

    if (analysis.tool === 'exiftool' && analysis.metadata) {
        content += `<div class="mockup-code p-4 code-output"><pre><code>${escapeHtml(analysis.metadata)}</code></pre></div>`;
    } else if (analysis.tool === 'strings' && analysis.strings) {
        content += `
            <div class="alert alert-info mb-4">
                <span>Total lines found: ${analysis.total_lines} (showing first 1000)</span>
            </div>
            <div class="mockup-code p-4 code-output"><pre><code>${escapeHtml(analysis.strings)}</code></pre></div>
        `;
    } else if (analysis.tool === 'binwalk') {
        content += `<div class="mockup-code p-4 code-output"><pre><code>${escapeHtml(analysis.output)}</code></pre></div>`;
        if (analysis.extracted_files?.length > 0) {
            content += createFileList('Extracted Files', analysis.extracted_files, analysisId);
        }
    } else if (analysis.tool === 'foremost') {
        content += `<div class="mockup-code p-4 code-output"><pre><code>${escapeHtml(analysis.output)}</code></pre></div>`;
        if (analysis.recovered_files?.length > 0) {
            content += createFileList('Recovered Files', analysis.recovered_files, analysisId);
        }
    } else if (analysis.output) {
        content += `<div class="mockup-code p-4 code-output"><pre><code>${escapeHtml(analysis.output)}</code></pre></div>`;
    }

    if (analysis.error?.trim()) {
        content += `
            <div class="alert alert-error mt-4">
                <span>Error: ${escapeHtml(analysis.error)}</span>
            </div>
        `;
    }

    content += '</div>';
    section.innerHTML = content;
    return section;
}

function createFileList(title, files, analysisId) {
    let html = `<div class="mt-4"><h3 class="font-bold mb-2">${title}</h3><ul class="menu bg-base-200 rounded-box">`;
    files.forEach(file => {
        const relativePath = file.split(analysisId + '/')[1];
        html += `
            <li>
                <a href="/download/${analysisId}/${relativePath}" target="_blank" class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    ${relativePath}
                </a>
            </li>
        `;
    });
    html += '</ul></div>';
    return html;
}

function displayFilters(filters, analysisId) {
    const filtersSection = document.getElementById('filtersSection');
    const filtersGrid = document.getElementById('filtersGrid');
    filtersGrid.innerHTML = '';

    const filterNames = {
        'grayscale': 'Grayscale',
        'high_contrast': 'High contrast',
        'edges': 'Edge detection',
        'brightness': 'Brightness',
        'inverted': 'Inverted',
        'sharpened': 'Sharpened'
    };

    Object.keys(filters).forEach(filterKey => {
        const card = document.createElement('div');
        card.className = 'card bg-base-200 shadow-lg';
        card.innerHTML = `
            <figure class="px-4 pt-4">
                <img src="/filter/${analysisId}/${filterKey}" class="rounded-lg" alt="${filterKey}">
            </figure>
            <div class="card-body">
                <h3 class="card-title text-sm">${filterNames[filterKey] || filterKey}</h3>
            </div>
        `;
        filtersGrid.appendChild(card);
    });

    filtersSection.classList.remove('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}