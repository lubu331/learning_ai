let quizQuestions = [];
let currentQuestionIndex = 0;
let score = 0;
let answerSubmitted = false;
let reviewItems = [];

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

const sendQuestionReportBtn = document.getElementById("sendQuestionReportBtn");
const questionReportNote = document.getElementById("questionReportNote");
const reportStatus = document.getElementById("reportStatus");

const finalScore = document.getElementById("finalScore");
const finalMessage = document.getElementById("finalMessage");
const reviewList = document.getElementById("reviewList");
const restartBtn = document.getElementById("restartBtn");

startQuizBtn.addEventListener("click", loadQuiz);
submitTextAnswerBtn.addEventListener("click", submitFreeTextAnswer);
nextQuestionBtn.addEventListener("click", goToNextQuestion);
restartBtn.addEventListener("click", restartApp);
sendQuestionReportBtn.addEventListener("click", sendQuestionReport);

freeTextInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !answerSubmitted) {
    submitFreeTextAnswer();
  }
});

fileUpload.addEventListener("change", () => {
  uploadedFiles.innerHTML = "";

  Array.from(fileUpload.files).forEach((file) => {
    const item = document.createElement("div");
    item.className = "file-pill";
    item.textContent = `📄 ${file.name}`;
    uploadedFiles.appendChild(item);
  });
});

async function loadQuiz() {
  const studentName = studentNameInput.value.trim();
  const gradeLevel = gradeLevelInput.value;
  const subject = subjectInput.value;
  const questionType = questionTypeInput.value;
  const limit = parseInt(limitInput.value, 10);

  if (!studentName) {
    statusMessage.textContent = "Please enter the student name.";
    return;
  }

  statusMessage.textContent = "Loading quiz...";

  try {
    const response = await fetch("/quiz", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        grade_level: gradeLevel,
        subject: subject,
        question_type: questionType,
        limit: limit
      })
    });

    const data = await response.json();

    if (!response.ok) {
      statusMessage.textContent = data.detail || "Could not load quiz.";
      return;
    }

    quizQuestions = data.questions;
    currentQuestionIndex = 0;
    score = 0;
    answerSubmitted = false;
    reviewItems = [];

    quizStudentName.textContent = studentName;
    scoreDisplay.textContent = "Score: 0";

    setupPage.classList.add("hidden");
    resultsPage.classList.add("hidden");
    quizPage.classList.remove("hidden");

    renderQuestion();
  } catch (error) {
    console.error(error);
    statusMessage.textContent = "Error loading quiz. Check the browser console.";
  }
}

function resetQuestionUI() {
  answerSubmitted = false;

  feedbackBox.classList.add("hidden");
  feedbackBox.classList.remove("correct", "incorrect");
  feedbackTitle.textContent = "Feedback";
  feedbackText.textContent = "";
  correctAnswerText.textContent = "";

  nextQuestionBtn.classList.add("hidden");

  freeTextInput.value = "";
  freeTextInput.disabled = false;
  submitTextAnswerBtn.disabled = false;

  multipleChoiceArea.innerHTML = "";

  questionReportNote.value = "";
  reportStatus.textContent = "";

  const radios = document.querySelectorAll("input[name='reportReason']");
  radios.forEach((radio) => {
    radio.checked = false;
  });
}

function renderQuestion() {
  const question = quizQuestions[currentQuestionIndex];
  resetQuestionUI();

  const total = quizQuestions.length;
  const current = currentQuestionIndex + 1;
  const progressPercent = Math.round(((current - 1) / total) * 100);

  questionCounter.textContent = `Question ${current} of ${total}`;
  questionNumber.textContent = `Question ${current}`;
  questionTag.textContent = question.question_tag || "";
  questionText.textContent = question.prompt_text;

  progressFill.style.width = `${progressPercent}%`;

  if (question.question_type === "free_text") {
    freeTextArea.classList.remove("hidden");
    multipleChoiceArea.classList.add("hidden");
    setTimeout(() => freeTextInput.focus(), 50);
  } else if (question.question_type === "multiple_choice") {
    freeTextArea.classList.add("hidden");
    multipleChoiceArea.classList.remove("hidden");
    renderChoices(question.choices || []);
  }
}

function renderChoices(choices) {
  multipleChoiceArea.innerHTML = "";

  choices.forEach((choice) => {
    const btn = document.createElement("button");
    btn.className = "option-btn";
    btn.textContent = `${choice.label}. ${choice.text}`;
    btn.dataset.label = choice.label;
    btn.dataset.correct = choice.is_correct ? "true" : "false";

    btn.addEventListener("click", () => {
      if (!answerSubmitted) {
        submitAnswer(choice.label);
      }
    });

    multipleChoiceArea.appendChild(btn);
  });
}

async function submitFreeTextAnswer() {
  const value = freeTextInput.value.trim();

  if (!value || answerSubmitted) {
    return;
  }

  await submitAnswer(value);
}

async function submitAnswer(studentAnswer) {
  const question = quizQuestions[currentQuestionIndex];

  try {
    const response = await fetch("/answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question: question,
        student_answer: studentAnswer
      })
    });

    const result = await response.json();

    if (!response.ok) {
      alert(result.detail || "Error submitting answer.");
      return;
    }

    answerSubmitted = true;

    if (result.is_correct) {
      score += 1;
      scoreDisplay.textContent = `Score: ${score}`;
    }

    if (question.question_type === "free_text") {
      freeTextInput.disabled = true;
      submitTextAnswerBtn.disabled = true;
    }

    if (question.question_type === "multiple_choice") {
      markChoiceResults(studentAnswer);
    }

    reviewItems.push({
      question: question.prompt_text,
      is_correct: result.is_correct,
      feedback: result.feedback_text,
      correct_answer: result.correct_answer_summary
    });

    showFeedback(result);
  } catch (error) {
    console.error(error);
    alert("Unexpected error submitting answer.");
  }
}

function markChoiceResults(selectedLabel) {
  const buttons = multipleChoiceArea.querySelectorAll(".option-btn");

  buttons.forEach((btn) => {
    btn.disabled = true;

    const label = btn.dataset.label;
    const isCorrect = btn.dataset.correct === "true";

    if (isCorrect) {
      btn.classList.add("correct");
    } else if (label === selectedLabel) {
      btn.classList.add("incorrect");
    }
  });
}

function showFeedback(result) {
  feedbackBox.classList.remove("hidden");
  feedbackBox.classList.remove("correct", "incorrect");

  if (result.is_correct) {
    feedbackBox.classList.add("correct");
    feedbackTitle.textContent = "Correct!";
  } else {
    feedbackBox.classList.add("incorrect");
    feedbackTitle.textContent = "Let’s review";
  }

  feedbackText.textContent = result.feedback_text;
  correctAnswerText.textContent = result.correct_answer_summary;

  nextQuestionBtn.classList.remove("hidden");
}

function goToNextQuestion() {
  currentQuestionIndex += 1;

  if (currentQuestionIndex >= quizQuestions.length) {
    showResults();
    return;
  }

  renderQuestion();
}

function showResults() {
  const total = quizQuestions.length;
  const percentage = total > 0 ? Math.round((score / total) * 100) : 0;

  progressFill.style.width = "100%";

  quizPage.classList.add("hidden");
  resultsPage.classList.remove("hidden");

  finalScore.textContent = `Score: ${score}/${total}`;

  if (percentage === 100) {
    finalMessage.textContent = "Amazing! Perfect score.";
  } else if (percentage >= 70) {
    finalMessage.textContent = "Great work! Keep practicing.";
  } else {
    finalMessage.textContent = "Good effort. Let’s review and try again.";
  }

  renderReviewList();
}

function renderReviewList() {
  reviewList.innerHTML = "";

  reviewItems.forEach((item) => {
    const div = document.createElement("div");
    div.className = `review-item ${item.is_correct ? "correct" : "incorrect"}`;

    div.innerHTML = `
      <strong>${escapeHtml(item.question)}</strong>
      <p>${escapeHtml(item.feedback)}</p>
      <p>${escapeHtml(item.correct_answer)}</p>
    `;

    reviewList.appendChild(div);
  });
}

function sendQuestionReport() {
  const question = quizQuestions[currentQuestionIndex];

  if (!question) {
    reportStatus.textContent = "No active question to report.";
    return;
  }

  const selectedReason = document.querySelector("input[name='reportReason']:checked");
  const note = questionReportNote.value.trim();

  if (!selectedReason && !note) {
    reportStatus.textContent = "Choose a reason or write a note first.";
    return;
  }

  console.log("Question report:", {
    question_code: question.question_code,
    question_tag: question.question_tag,
    reason: selectedReason ? selectedReason.value : null,
    note: note
  });

  reportStatus.textContent = "Feedback saved locally in browser console for now.";
}

function restartApp() {
  quizQuestions = [];
  currentQuestionIndex = 0;
  score = 0;
  answerSubmitted = false;
  reviewItems = [];

  resultsPage.classList.add("hidden");
  quizPage.classList.add("hidden");
  setupPage.classList.remove("hidden");

  statusMessage.textContent = "";
  studentNameInput.focus();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}