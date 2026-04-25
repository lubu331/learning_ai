let quizQuestions = [];
let currentQuestionIndex = 0;
let score = 0;
let answerSubmitted = false;

const setupPage = document.getElementById("setupPage");
const quizPage = document.getElementById("quizPage");
const resultsPage = document.getElementById("resultsPage");

const startQuizBtn = document.getElementById("startQuizBtn");
const statusMessage = document.getElementById("statusMessage");

const studentNameInput = document.getElementById("studentName");
const gradeLevelInput = document.getElementById("gradeLevel");
const subjectInput = document.getElementById("subject");
const questionTypeInput = document.getElementById("questionType");
const limitInput = document.getElementById("limit");
const fileUpload = document.getElementById("fileUpload");
const uploadedFiles = document.getElementById("uploadedFiles");

const existingPdfSelect = document.getElementById("existingPdf");

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

const finalScore = document.getElementById("finalScore");
const restartBtn = document.getElementById("restartBtn");

startQuizBtn.addEventListener("click", loadQuiz);
submitTextAnswerBtn.addEventListener("click", submitFreeTextAnswer);
nextQuestionBtn.addEventListener("click", goToNextQuestion);
restartBtn.addEventListener("click", restartApp);

fileUpload.addEventListener("change", () => {
  uploadedFiles.innerHTML = "";

  Array.from(fileUpload.files).forEach((file) => {
    const item = document.createElement("div");
    item.className = "file-pill";
    item.textContent = file.name;
    uploadedFiles.appendChild(item);
  });
});

async function loadExistingPdfs() {
  const response = await fetch("/pdfs");
  const data = await response.json();

  existingPdfSelect.innerHTML = `<option value="">Upload a new PDF</option>`;

  data.files.forEach((file) => {
    const option = document.createElement("option");
    option.value = file;
    option.textContent = file;
    existingPdfSelect.appendChild(option);
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
    statusMessage.textContent = "Error generating quiz. Check Ollama and terminal logs.";
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
  questionNumber.textContent = `Question ${current}`;
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

loadExistingPdfs();