const fileInput = document.getElementById("fileInput");
// const labelForFileInput = document.querySelector("label[for='fileInput'] .text-truncate");
const resultBox = document.getElementById("resultBox");
const fileNameDisplay = document.getElementById("fileNameDisplay");

const analyserBtn = document.getElementById("analyserBtn");
fileInput.addEventListener("change", function () {
  if (this.files.length > 0) {
    analyserBtn.disabled = false; // activer si fichier choisi
  } else {
    analyserBtn.disabled = true;  // désactiver sinon
  }
});


/*fileInput.addEventListener("change", function () {
  if (this.files.length > 0) {
    const fileName = this.files[0].name;
    labelForFileInput.textContent = fileName.length > 30 ? fileName.substring(0, 27) + '...' : fileName;
    labelForFileInput.setAttribute('title', fileName); // Add tooltip for long filenames
    analyserBtn.disabled = false; // Enable button if file is selected
  } else {
    labelForFileInput.textContent = "Importer un fichier...";
    labelForFileInput.removeAttribute('title');
    analyserBtn.disabled = true; // Disable button if no file is selected
  }
});*/

/*analyserBtn.addEventListener("click", function () {
  if (!fileInput.files.length) {
    resultBox.style.display = "block";
    resultBox.className = "result-box error shadow-lg"; // Add error class
    resultBox.innerHTML = "<span class='fw-bold'>⚠️ Oops!</span> Veuillez importer un fichier à analyser.";
  } else {
    const fileName = fileInput.files[0].name;
    resultBox.style.display = "block";
    resultBox.className = "result-box success shadow-lg"; // Add success class
    resultBox.innerHTML = `<span class='fw-bold'>🚀 Envoi en cours...</span> Fichier <strong class='text-decoration-underline'>${fileName}</strong> prêt pour l'analyse.`;

    // Simulate analysis process (replace with actual AJAX call to your backend)
    setTimeout(() => {
      const isPhishing = Math.random() > 0.5; // Simulate random result
      if (isPhishing) {
        resultBox.className = "result-box error shadow-lg";
        resultBox.innerHTML = `<span class='fw-bold'>🚨 ATTENTION!</span> Ce fichier semble contenir des éléments de phishing.`;
      } else {
        resultBox.className = "result-box success shadow-lg";
        resultBox.innerHTML = `<span class='fw-bold'>✅ SÉCURISÉ!</span> Ce fichier semble légitime.`;
      }
    }, 2000); // Simulate a 2-second analysis time
  }
});
*/
// Initially disable the analyze button
//analyserBtn.disabled = true;