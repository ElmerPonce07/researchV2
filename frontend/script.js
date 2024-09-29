
document.getElementById("searchBtn").onclick = async function () {
  const keyword = document.getElementById("keyword").value;
  const response = await fetch("/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keyword }),
  });
  const data = await response.json();
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = ""; // Clear previous results

  if (data.urls) {
    data.urls.forEach((url) => {
      const urlElement = document.createElement("a"); // Create an 'a' element for links
      urlElement.className = "result-link"; // Add the result-link class
      urlElement.href = url; // Set the href to the URL
      urlElement.innerText = url;
      urlElement.target = "_blank"; // Open in a new tab
      urlElement.onclick = async function (event) {
        event.preventDefault(); // Prevent the default action to allow fetching summary
        const summaryResponse = await fetch("/summarize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url }),
        });
        const summaryData = await summaryResponse.json();
        document.getElementById("summary").innerText = summaryData.summary;
      };
      resultsDiv.appendChild(urlElement);
    });
  } else {
    resultsDiv.innerText = data.error || "No results found.";
  }
};

document.getElementById("translateBtn").onclick = async function () {
  const selectedLanguage = document.getElementById("languageSelect").value;
  const summaryText = document.getElementById("summary").innerText; // Get the summary text
  const response = await fetch("/translate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ summary: summaryText, language: selectedLanguage }),
  });
  const data = await response.json();
  document.getElementById("translatedSummary").innerText = data.translated; // Display translated summary
};
