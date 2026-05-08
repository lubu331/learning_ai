let quizQuestions = [];
let currentQuestionIndex = 0;
let score = 0;
let answerSubmitted = false;
let savedPdfFiles = [];
let curriculumTopics = {};

// DOM Elements - Setup Page
const setupPage = document.getElementById("setupPage");
const startQuizBtn = document.getElementById("startQuizBtn");
const statusMessage = document.getElementById("statusMessage");
const studentNameInput = document.getElementById("studentName");
const gradeLevelInput = document.getElementById("gradeLevel");
const subjectInput = document.getElementById("subject");
const topicInput = document.getElementById("topic");
const questionTypeInput = document.getElementById("questionType");
const limitInput = document.getElementById("limit");
const fileUpload = document.getElementById("fileUpload");
const uploadedFiles = document.getElementById("uploadedFiles");
const existingPdfSelect = document.getElementById("existingPdf");
const pdfLibrary = document.getElementById("pdfLibrary");
const refreshPdfBtn = document.getElementById("refreshPdfBtn");

// DOM Elements - Quiz Page
const quizPage = document.getElementById("quizPage");
const quizStudentName = document.getElementById("quizStudentName");
const scoreDisplay = document.getElementById("scoreDisplay");
const questionCounter = document.getElementById("questionCounter");
const questionTag = document.getElementById("questionTag");
const progressFill = document.getElementById("progressFill");
const questionNumber = document.getElementById("questionNumber");
const questionText = document.getElementById("questionText");
const freeTextArea = document.getElementById("freeTextArea");
const freeTextInput = document.getElementById("freeTextInput");
const submitTextAnswerBtn = document.getElementById("submitTextAnswerBtn");
const multipleChoiceArea = document.getElementById("multipleChoiceArea");
const feedbackBox = document.getElementById("feedbackBox");
const feedbackTitle = document.getElementById("feedbackTitle");
const feedbackText = document.getElementById("feedbackText");
const correctAnswerText = document.getElementById("correctAnswerText");
const nextQuestionBtn = document.getElementById("nextQuestionBtn");

// DOM Elements - Results Page
const resultsPage = document.getElementById("resultsPage");
const finalScore = document.getElementById("finalScore");
const restartBtn = document.getElementById("restartBtn");

// DOM Elements - Feedback Modal
const feedbackModal = document.getElementById("feedbackModal");
const openFeedbackModalBtn = document.getElementById("openFeedbackModalBtn");
const closeFeedbackModalBtn = document.getElementById("closeFeedbackModalBtn");
const submitFeedbackBtn = document.getElementById("submitFeedbackBtn");
const feedbackReasons = document.querySelectorAll(".feedback-reason");
const feedbackNoteInput = document.getElementById("feedbackNote");
const feedbackSuccessMsg = document.getElementById("feedbackSuccessMsg");

// Event Listeners
startQuizBtn.addEventListener("click", loadQuiz);
submitTextAnswerBtn.addEventListener("click", submitFreeTextAnswer);
nextQuestionBtn.addEventListener("click", goToNextQuestion);
restartBtn.addEventListener("click", restartApp);
refreshPdfBtn.addEventListener("click", loadExistingPdfs);
subjectInput.addEventListener("change", renderTopicOptions);
existingPdfSelect.addEventListener("change", () => {
  if (existingPdfSelect.value) {
    fileUpload.value = "";
    uploadedFiles.innerHTML = "";
  }

  renderSelectedPdf();
});

fileUpload.addEventListener("change", () => {
  uploadedFiles.innerHTML = "";
  existingPdfSelect.value = "";
  renderSelectedPdf();

  Array.from(fileUpload.files).forEach((file) => {
    const item = document.createElement("div");
    item.className = "file-pill";
    item.textContent = `Ready to upload: ${file.name}`;
    uploadedFiles.appendChild(item);
  });
});

// Modal Event Listeners
openFeedbackModalBtn.addEventListener("click", openFeedbackModal);
closeFeedbackModalBtn.addEventListener("click", closeFeedbackModal);
submitFeedbackBtn.addEventListener("click", submitFeedback);

// Close modal if clicking outside the card
feedbackModal.addEventListener("click", (e) => {
  if (e.target === feedbackModal) {
    closeFeedbackModal();
  }
});

// Reason Selection Logic
feedbackReasons.forEach((reasonBtn) => {
  reasonBtn.addEventListener("click", () => {
    // Remove active class from all
    feedbackReasons.forEach((btn) => btn.classList.remove("active"));
    // Add active class to clicked
    reasonBtn.classList.add("active");
  });
});

async function loadExistingPdfs() {
  pdfLibrary.innerHTML = `<p class="empty-library">Loading saved PDFs...</p>`;

  try {
    const response = await fetch("/pdfs");

    if (!response.ok) {
      throw new Error("Could not load saved PDFs.");
    }

    const data = await response.json();
    const files = data.files.map(normalizePdfFile);
    savedPdfFiles = files;

    existingPdfSelect.innerHTML = `<option value="">Upload a new PDF</option>`;

    files.forEach((file) => {
      const option = document.createElement("option");
      option.value = file.name;
      option.textContent = file.name;
      existingPdfSelect.appendChild(option);
    });

    renderSelectedPdf();
  } catch (error) {
    console.error(error);
    pdfLibrary.innerHTML = `<p class="library-error">Could not load saved PDFs. Check the server console.</p>`;
  }
}

async function loadCurriculum() {
  try {
    const response = await fetch("/curriculum");

    if (!response.ok) {
      throw new Error("Could not load curriculum topics.");
    }

    const data = await response.json();
    curriculumTopics = data.subjects || {};
  } catch (error) {
    console.error(error);
    curriculumTopics = {
      math: [
        {id: "addition", label: "Addition"},
        {id: "subtraction", label: "Subtraction"},
        {id: "word_problems", label: "Word problems"},
      ],
      english: [
        {id: "reading_comprehension", label: "Reading comprehension"},
        {id: "vocabulary", label: "Vocabulary"},
        {id: "grammar", label: "Grammar"},
        {id: "sentence_writing", label: "Sentence writing"},
      ],
      sociales_colombia: [
        {id: "colombian_geography", label: "Colombian geography"},
        {id: "colombian_history", label: "Colombian history"},
        {id: "civic_behavior", label: "Civic behavior and society"},
      ],
    };
  }

  renderTopicOptions();
}

function renderTopicOptions() {
  const topics = curriculumTopics[subjectInput.value] || [];
  topicInput.innerHTML = "";

  topics.forEach((topic) => {
    const option = document.createElement("option");
    option.value = topic.id;
    option.textContent = topic.label;
    topicInput.appendChild(option);
  });

  if (!topics.length) {
    const option = document.createElement("option");
    option.value = "general";
    option.textContent = "General practice";
    topicInput.appendChild(option);
  }
}

function normalizePdfFile(file) {
  if (typeof file === "string") {
    return {
      name: file,
      size_bytes: 0,
      modified_at: "",
    };
  }

  return file;
}

function renderSelectedPdf() {
  const selected = existingPdfSelect.value;
  pdfLibrary.innerHTML = "";

  if (!savedPdfFiles.length) {
    pdfLibrary.innerHTML = `<p class="empty-library">No saved PDFs yet. Upload one and it will appear here next time.</p>`;
    return;
  }

  if (!selected) {
    pdfLibrary.innerHTML = `<p class="empty-library">Select a saved PDF from the dropdown or upload a new worksheet.</p>`;
    return;
  }

  const file = savedPdfFiles.find((item) => item.name === selected);

  if (!file) {
    pdfLibrary.innerHTML = `<p class="library-error">That saved PDF is no longer available. Refresh the list.</p>`;
    return;
  }

  const selectedCard = document.createElement("div");
  selectedCard.className = "selected-pdf-summary";

  const title = document.createElement("span");
  title.className = "pdf-title";
  title.textContent = file.name;

  const meta = document.createElement("span");
  meta.className = "pdf-meta";
  meta.textContent = formatPdfMeta(file);

  selectedCard.append(title, meta);
  pdfLibrary.appendChild(selectedCard);
}

function formatPdfMeta(file) {
  const details = [];

  if (file.size_bytes) {
    details.push(formatBytes(file.size_bytes));
  }

  if (file.modified_at) {
    details.push(`Updated ${formatDate(file.modified_at)}`);
  }

  return details.join(" · ") || "Saved worksheet";
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(value) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "recently";
  }

  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

async function loadQuiz() {
  const studentName = studentNameInput.value.trim();
  if (!studentName) {
    statusMessage.textContent = "Please enter the student name.";
    return;
  }

  const formData = new FormData();
  formData.append("grade_level", gradeLevelInput.value);
  formData.append("subject", subjectInput.value);
  formData.append("topic", topicInput.value);
  formData.append("question_type", questionTypeInput.value);
  formData.append("limit", limitInput.value);

  if (existingPdfSelect.value) {
    formData.append("existing_pdf", existingPdfSelect.value);
  } else if (fileUpload.files.length > 0) {
    formData.append("file", fileUpload.files[0]);
  } else {
    statusMessage.textContent = "Upload a PDF or select an existing one.";
    return;
  }

  statusMessage.textContent = "Generating quiz with Ollama...";

  try {
    const response = await fetch("/quiz", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      statusMessage.textContent = data.detail || "Could not generate quiz.";
      return;
    }

    quizQuestions = data.questions;
    currentQuestionIndex = 0;
    score = 0;
    answerSubmitted = false;

    quizStudentName.textContent = studentName;
    scoreDisplay.textContent = "Score: 0";

    setupPage.classList.add("hidden");
    resultsPage.classList.add("hidden");
    quizPage.classList.remove("hidden");

    renderQuestion();
  } catch (error) {
    console.error(error);
    statusMessage.textContent = "Could not reach the quiz generator. Make sure Ollama is running and try fewer questions.";

  }
}

function renderQuestion() {
  const question = quizQuestions[currentQuestionIndex];
  const total = quizQuestions.length;
  const current = currentQuestionIndex + 1;

  answerSubmitted = false;

  feedbackBox.classList.add("hidden");
  nextQuestionBtn.classList.add("hidden");
  multipleChoiceArea.innerHTML = "";
  freeTextInput.value = "";
  freeTextInput.disabled = false;
  submitTextAnswerBtn.disabled = false;

  questionCounter.textContent = `Question ${current} of ${total}`;
  questionNumber.textContent = `Question ${current}`

    questionTag.textContent = question.question_tag || "";
  questionText.textContent = question.prompt_text;
  progressFill.style.width = `${Math.round(((current - 1) / total) * 100)}%`;

  if (question.question_type === "free_text") {
    freeTextArea.classList.remove("hidden");
    multipleChoiceArea.classList.add("hidden");
  } else {
    freeTextArea.classList.add("hidden");
    multipleChoiceArea.classList.remove("hidden");

    question.choices.forEach((choice) => {
      const btn = document.createElement("button");
      btn.className = "option-btn";
      btn.textContent = `${choice.label}. ${choice.text}`;
      btn.addEventListener("click", () => submitAnswer(choice.label));
      multipleChoiceArea.appendChild(btn);
    });
  }
}

async function submitFreeTextAnswer() {
  const answer = freeTextInput.value.trim();
  if (!answer) return;
  await submitAnswer(answer);
}

async function submitAnswer(studentAnswer) {
  if (answerSubmitted) return;

  const question = quizQuestions[currentQuestionIndex];

  const response = await fetch("/answer", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      question,
      student_answer: studentAnswer,
    }),
  });

  const result = await response.json();
  answerSubmitted = true;

  if (result.is_correct) {
    score++;
    scoreDisplay.textContent = `Score: ${score}`;
  }

  feedbackBox.classList.remove("hidden");
  feedbackTitle.textContent = result.is_correct ? "Correct!" : "Let’s review";
  feedbackText.textContent = result.feedback_text;
  correctAnswerText.textContent = result.correct_answer_summary;

  nextQuestionBtn.classList.remove("hidden");

  freeTextInput.disabled = true;
  submitTextAnswerBtn.disabled = true;
}

function goToNextQuestion() {
  currentQuestionIndex++;
  if (currentQuestionIndex >= quizQuestions.length) {
    showResults();
    return;
  }
  renderQuestion();
}

function showResults() {
  quizPage.classList.add("hidden");
  resultsPage.classList.remove("hidden");
  finalScore.textContent = `Score: ${score}/${quizQuestions.length}`;
}

function restartApp() {
  resultsPage.classList.add("hidden");
  quizPage.classList.add("hidden");
  setupPage.classList.remove("hidden");
  statusMessage.textContent = "";
  loadExistingPdfs();
}

// --- FEEDBACK MODAL LOGIC ---

function openFeedbackModal() {
  feedbackModal.classList.remove("hidden");
  feedbackSuccessMsg.classList.add("hidden");
  submitFeedbackBtn.disabled = false;
  feedbackNoteInput.value = "";

  // Reset reason selection
  feedbackReasons.forEach((btn) => btn.classList.remove("active"));
}

function closeFeedbackModal() {
  feedbackModal.classList.add("hidden");
}

async function submitFeedback() {
  const selectedReason = document.querySelector(".feedback-reason.active");
  const question = quizQuestions[currentQuestionIndex];

  if (!selectedReason || !question) {
    feedbackSuccessMsg.textContent = "Choose a reason first.";
    feedbackSuccessMsg.classList.remove("hidden");
    return;
  }

  submitFeedbackBtn.disabled = true;

  try {
    const response = await fetch("/submit-feedback", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        question_code: question.question_code || "",
        prompt_text: question.prompt_text || "",
        reason: selectedReason.dataset.reason,
        user_note: feedbackNoteInput.value.trim(),
      }),
    });

    if (!response.ok) {
      throw new Error("Feedback request failed.");
    }

    feedbackSuccessMsg.textContent = "Feedback sent.";
    feedbackSuccessMsg.classList.remove("hidden");
  } catch (error) {
    console.error(error);
    feedbackSuccessMsg.textContent = "Could not send feedback.";
    feedbackSuccessMsg.classList.remove("hidden");
    submitFeedbackBtn.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadCurriculum();
  loadExistingPdfs();
});
