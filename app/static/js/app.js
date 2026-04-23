let quizQuestions = [];
let currentQuestionIndex = 0;
let currentQuizAttemptId = null;
let answerSubmitted = false;

const loadQuizBtn = document.getElementById("loadQuizBtn");
const statusMessage = document.getElementById("statusMessage");
const quizCard = document.getElementById("quizCard");
const questionCounter = document.getElementById("questionCounter");
const questionMeta = document.getElementById("questionMeta");
const questionText = document.getElementById("questionText");

const freeTextArea = document.getElementById("freeTextArea");
const freeTextInput = document.getElementById("freeTextInput");
const submitTextAnswerBtn = document.getElementById("submitTextAnswerBtn");

const multipleChoiceArea = document.getElementById("multipleChoiceArea");

const feedbackBox = document.getElementById("feedbackBox");
const feedbackText = document.getElementById("feedbackText");
const correctAnswerText = document.getElementById("correctAnswerText");
const nextQuestionBtn = document.getElementById("nextQuestionBtn");

loadQuizBtn.addEventListener("click", loadQuiz);
submitTextAnswerBtn.addEventListener("click", submitFreeTextAnswer);
nextQuestionBtn.addEventListener("click", goToNextQuestion);

async function loadQuiz() {
  const gradeLevel = document.getElementById("gradeLevel").value;
  const subject = document.getElementById("subject").value;
  const questionType = document.getElementById("questionType").value;
  const limit = parseInt(document.getElementById("limit").value, 10);

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
      quizCard.classList.add("hidden");
      return;
    }

    quizQuestions = data.questions;
    currentQuizAttemptId = data.quiz_attempt_id;
    currentQuestionIndex = 0;
    statusMessage.textContent = `Quiz loaded. ${quizQuestions.length} question(s) ready.`;
    quizCard.classList.remove("hidden");
    renderQuestion();
  } catch (error) {
    statusMessage.textContent = "Error loading quiz.";
    console.error(error);
  }
}

function renderQuestion() {
  const question = quizQuestions[currentQuestionIndex];
  answerSubmitted = false;

  questionCounter.textContent = `Question ${currentQuestionIndex + 1} of ${quizQuestions.length}`;
  questionMeta.textContent = `${question.subject} • ${question.topic}`;
  questionText.textContent = question.prompt_text;

  feedbackBox.classList.add("hidden");
  feedbackBox.classList.remove("correct", "incorrect");
  nextQuestionBtn.classList.add("hidden");
  freeTextInput.value = "";
  multipleChoiceArea.innerHTML = "";

  if (question.question_type === "free_text") {
    freeTextArea.classList.remove("hidden");
    multipleChoiceArea.classList.add("hidden");
  } else if (question.question_type === "multiple_choice") {
    freeTextArea.classList.add("hidden");
    multipleChoiceArea.classList.remove("hidden");
    renderChoices(question.choices);
  }
}

function renderChoices(choices) {
  multipleChoiceArea.innerHTML = "";

  choices.forEach(choice => {
    const btn = document.createElement("button");
    btn.className = "choice-btn";
    btn.textContent = `${choice.label}. ${choice.text}`;
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
  if (!value) return;
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
    showFeedback(result);
  } catch (error) {
    console.error(error);
    alert("Unexpected error submitting answer.");
  }
}

function showFeedback(result) {
  feedbackText.textContent = result.feedback_text;
  correctAnswerText.textContent = result.correct_answer_summary;
  feedbackBox.classList.remove("hidden");

  if (result.is_correct) {
    feedbackBox.classList.add("correct");
  } else {
    feedbackBox.classList.add("incorrect");
  }

  nextQuestionBtn.classList.remove("hidden");
}

function goToNextQuestion() {
  // 🔴 Reset UI immediately BEFORE changing question
  feedbackBox.classList.add("hidden");
  feedbackBox.classList.remove("correct", "incorrect");
  nextQuestionBtn.classList.add("hidden");

  freeTextInput.value = "";
  multipleChoiceArea.innerHTML = "";
  answerSubmitted = false;

  currentQuestionIndex += 1;

  if (currentQuestionIndex >= quizQuestions.length) {
    questionText.textContent = "Quiz finished. Great job!";
    questionMeta.textContent = "";
    questionCounter.textContent = "";
    freeTextArea.classList.add("hidden");
    multipleChoiceArea.classList.add("hidden");
    return;
  }

  renderQuestion();
}