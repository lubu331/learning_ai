* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: #f4f7fb;
  color: #1f2937;
}

.container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
}

h1 {
  margin-bottom: 8px;
}

.subtitle {
  margin-top: 0;
  color: #6b7280;
}

.card {
  background: white;
  border-radius: 14px;
  padding: 24px;
  margin-top: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: 8px;
  font-weight: bold;
}

select,
input[type="number"],
input[type="text"] {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 10px;
  font-size: 16px;
}

button {
  padding: 12px 18px;
  border: none;
  border-radius: 10px;
  background: #2563eb;
  color: white;
  font-size: 16px;
  cursor: pointer;
}

button:hover {
  background: #1d4ed8;
}

.hidden {
  display: none;
}

.status {
  margin-top: 12px;
  color: #374151;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-meta {
  color: #6b7280;
  margin-bottom: 10px;
}

.question-text {
  font-size: 22px;
  margin: 20px 0;
}

.choices {
  display: grid;
  gap: 12px;
}

.choice-btn {
  text-align: left;
  background: #eef2ff;
  color: #111827;
  border: 1px solid #c7d2fe;
}

.choice-btn:hover {
  background: #dbeafe;
}

.feedback {
  margin-top: 20px;
  padding: 16px;
  border-radius: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.correct {
  border-color: #86efac;
  background: #f0fdf4;
}

.incorrect {
  border-color: #fca5a5;
  background: #fef2f2;
}

#nextQuestionBtn {
  margin-top: 16px;
}