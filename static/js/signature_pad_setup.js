// static/js/signature_pad_setup.js
// Requires SignaturePad library: include signature_pad.umd.min.js before this script

const signatureConfigs = {};

function initSignaturePad(canvasId, inputId) {
  const canvas = document.getElementById(canvasId);
  const input = document.getElementById(inputId);

  // Adjust canvas for high-DPI screens
  function resizeCanvas() {
    const ratio = Math.max(window.devicePixelRatio || 1, 1);
    canvas.width = canvas.offsetWidth * ratio;
    canvas.height = canvas.offsetHeight * ratio;
    canvas.getContext("2d").scale(ratio, ratio);
    if (signatureConfigs[canvasId]?.pad) {
      signatureConfigs[canvasId].pad.clear(); // reset if already configured
    }
  }

  window.addEventListener("resize", resizeCanvas);
  resizeCanvas();

  // Initialize SignaturePad
  const pad = new SignaturePad(canvas, {
    backgroundColor: "rgba(255, 255, 255, 0)",
    penColor: "rgb(0, 0, 0)",
  });

  // Common function to push the DataURL into the hidden input
  function updateInput() {
    if (!pad.isEmpty()) {
      input.value = pad.toDataURL();
    }
  }

  // 1) On SignaturePad stroke end callback
  pad.onEnd = updateInput;

  // 2) Also catch pointer/touch end on canvas itself
  canvas.addEventListener("mouseup", updateInput);
  canvas.addEventListener("touchend", updateInput);

  signatureConfigs[canvasId] = { pad, input };
}

function clearMediaPad() {
  const cfg = signatureConfigs["media-pad"];
  if (cfg) {
    cfg.pad.clear();
    cfg.input.value = "";
  }
}

function clearWaiverPad() {
  const cfg = signatureConfigs["waiver-pad"];
  if (cfg) {
    cfg.pad.clear();
    cfg.input.value = "";
  }
}
