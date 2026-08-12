async function analyzeCode() {
  const code  = document.getElementById('broken-code').value.trim();
  const error = document.getElementById('error-msg').value.trim();
  const btn   = document.getElementById('analyze-btn');
  const btnText    = document.getElementById('btn-text');
  const btnSpinner = document.getElementById('btn-spinner');
  const errorBanner = document.getElementById('error-banner');
  const results = document.getElementById('results');

  // Validate
  if (!code)  { showError('Please paste your broken code.'); return; }
  if (!error) { showError('Please paste the error message.'); return; }

  // Loading state
  btn.disabled = true;
  btnText.textContent = 'Analyzing...';
  btnSpinner.classList.remove('hidden');
  errorBanner.classList.add('hidden');
  results.classList.add('hidden');

  try {
    const res = await fetch('/api/debug', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ broken_code: code, error_message: error })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Server error');
    }

    const data = await res.json();
    renderResults(data);

  } catch (err) {
    showError(err.message || 'Something went wrong. Check your API key.');
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Analyze & Debug';
    btnSpinner.classList.add('hidden');
  }
}

function renderResults(data) {
  // Meta badges
  setText('r-language',  data.language.toUpperCase());
  setText('r-error-type', data.error_type);
  setText('r-confidence', `Confidence: ${data.confidence_score}%`);

  // Teaching loop badge
  const loopBadge = document.getElementById('r-loop');
  if (data.teaching_loop_used) {
    loopBadge.textContent = 'Teaching loop used';
    loopBadge.style.display = 'inline-block';
  } else {
    loopBadge.style.display = 'none';
  }

  // Root cause + senior tip
  setText('r-root-cause', data.root_cause);
  setText('r-senior-tip', `Senior tip: ${data.senior_tip}`);

  // Explanation
  setText('r-explanation', data.plain_explanation);

  // Fix A
  document.getElementById('r-fix-a').textContent = data.fix_a.code;
  setText('r-fix-a-pros', data.fix_a.pros);
  setText('r-fix-a-cons', data.fix_a.cons);

  // Fix B
  document.getElementById('r-fix-b').textContent = data.fix_b.code;
  setText('r-fix-b-pros', data.fix_b.pros);
  setText('r-fix-b-cons', data.fix_b.cons);

  // Recommended badge
  document.getElementById('rec-a').classList.toggle('hidden', data.recommended_fix !== 'A');
  document.getElementById('rec-b').classList.toggle('hidden', data.recommended_fix !== 'B');
  document.getElementById('fix-a-card').classList.toggle('highlighted', data.recommended_fix === 'A');
  document.getElementById('fix-b-card').classList.toggle('highlighted', data.recommended_fix === 'B');

  // Test + docstring
  document.getElementById('r-test').textContent = data.regression_test;
  document.getElementById('r-docstring').textContent = data.docstring;

  // Show results
  document.getElementById('results').classList.remove('hidden');
  document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text || '';
}

function showError(msg) {
  const banner = document.getElementById('error-banner');
  banner.textContent = msg;
  banner.classList.remove('hidden');
}

function copyCode(elementId) {
  const text = document.getElementById(elementId).textContent;
  navigator.clipboard.writeText(text).then(() => {
    // find the copy button near this element and flash it
    const el = document.getElementById(elementId);
    const btn = el.closest('.fix-card, .card')?.querySelector('.copy-btn');
    if (btn) {
      const orig = btn.textContent;
      btn.textContent = 'Copied!';
      setTimeout(() => { btn.textContent = orig; }, 1500);
    }
  });
}

// Allow Ctrl+Enter to submit
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') analyzeCode();
});
