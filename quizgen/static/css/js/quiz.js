// Quiz state variables
let currentQuiz = null
let currentQuestionIndex = 0
let userAnswers = []
let quizStartTime = null
let quizEndTime = null

// Function declarations
function getQuestions(category, subcategory, questionCount, difficulty) {
  // Placeholder function for getting questions
  // This should be replaced with actual implementation
  return []
}

function saveQuizResult(category, subcategory, scorePercentage, totalQuestions) {
  // Placeholder function for saving quiz results
  // This should be replaced with actual implementation
}

// Initialize quiz page
document.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname.includes("quiz.html")) {
    initializeQuiz()
  }
})

function initializeQuiz() {
  // Get quiz settings from sessionStorage
  const quizSettings = JSON.parse(sessionStorage.getItem("currentQuizSettings"))

  if (!quizSettings) {
    alert("No quiz selected. Redirecting to categories.")
    window.location.href = "categories.html"
    return
  }

  // Load questions
  const questions = getQuestions(
    quizSettings.category,
    quizSettings.subcategory,
    quizSettings.questionCount,
    quizSettings.difficulty,
  )

  if (questions.length === 0) {
    alert("No questions available for this selection.")
    window.location.href = "categories.html"
    return
  }

  // Initialize quiz state
  currentQuiz = {
    settings: quizSettings,
    questions: questions,
    totalQuestions: questions.length,
  }

  userAnswers = new Array(questions.length).fill(null)
  currentQuestionIndex = 0
  quizStartTime = new Date()

  // Update UI
  updateQuizInfo()
  displayQuestion()
}

function updateQuizInfo() {
  document.getElementById("quizCategory").textContent =
    `${currentQuiz.settings.category} - ${currentQuiz.settings.subcategory}`
}

function displayQuestion() {
  const question = currentQuiz.questions[currentQuestionIndex]
  const questionNumber = currentQuestionIndex + 1
  const totalQuestions = currentQuiz.totalQuestions

  // Update progress
  const progressPercentage = (questionNumber / totalQuestions) * 100
  document.getElementById("progressFill").style.width = progressPercentage + "%"
  document.getElementById("progressText").textContent = `Question ${questionNumber} of ${totalQuestions}`
  document.getElementById("quizProgress").textContent = `Question ${questionNumber} of ${totalQuestions}`

  // Update question text
  document.getElementById("questionText").textContent = question.question

  // Create answer options
  const answersContainer = document.getElementById("answersContainer")
  answersContainer.innerHTML = ""

  question.options.forEach((option, index) => {
    const answerDiv = document.createElement("div")
    answerDiv.className = "answer-option"
    answerDiv.onclick = () => selectAnswer(index)

    const isSelected = userAnswers[currentQuestionIndex] === index
    if (isSelected) {
      answerDiv.classList.add("selected")
    }

    answerDiv.innerHTML = `
      <div class="answer-letter">${String.fromCharCode(65 + index)}</div>
      <div class="answer-text">${option}</div>
    `

    answersContainer.appendChild(answerDiv)
  })

  // Update navigation buttons
  updateNavigationButtons()
}

function selectAnswer(answerIndex) {
  userAnswers[currentQuestionIndex] = answerIndex

  // Update UI
  const answerOptions = document.querySelectorAll(".answer-option")
  answerOptions.forEach((option, index) => {
    option.classList.toggle("selected", index === answerIndex)
  })

  // Enable next button
  updateNavigationButtons()
}

function updateNavigationButtons() {
  const prevBtn = document.getElementById("prevBtn")
  const nextBtn = document.getElementById("nextBtn")

  // Previous button
  prevBtn.disabled = currentQuestionIndex === 0

  // Next button
  const hasAnswer = userAnswers[currentQuestionIndex] !== null
  nextBtn.disabled = !hasAnswer

  // Update next button text
  if (currentQuestionIndex === currentQuiz.totalQuestions - 1) {
    nextBtn.textContent = "Finish Quiz"
  } else {
    nextBtn.textContent = "Next Question"
  }
}

function previousQuestion() {
  if (currentQuestionIndex > 0) {
    currentQuestionIndex--
    displayQuestion()
  }
}

function nextQuestion() {
  if (currentQuestionIndex < currentQuiz.totalQuestions - 1) {
    currentQuestionIndex++
    displayQuestion()
  } else {
    finishQuiz()
  }
}

function finishQuiz() {
  quizEndTime = new Date()

  // Calculate results
  const results = calculateResults()

  // Save quiz result
  saveQuizResult(
    currentQuiz.settings.category,
    currentQuiz.settings.subcategory,
    results.scorePercentage,
    currentQuiz.totalQuestions,
  )

  // Show results
  displayResults(results)
}

function calculateResults() {
  let correctCount = 0
  const reviewItems = []

  currentQuiz.questions.forEach((question, index) => {
    const userAnswer = userAnswers[index]
    const isCorrect = userAnswer === question.correct

    if (isCorrect) {
      correctCount++
    }

    reviewItems.push({
      questionNumber: index + 1,
      question: question.question,
      userAnswer: userAnswer !== null ? question.options[userAnswer] : "Not answered",
      correctAnswer: question.options[question.correct],
      isCorrect: isCorrect,
    })
  })

  const scorePercentage = Math.round((correctCount / currentQuiz.totalQuestions) * 100)
  const timeTaken = Math.floor((quizEndTime - quizStartTime) / 1000)

  return {
    correctCount,
    totalQuestions: currentQuiz.totalQuestions,
    scorePercentage,
    timeTaken,
    reviewItems,
  }
}

function displayResults(results) {
  // Hide quiz section, show results section
  document.getElementById("quizSection").style.display = "none"
  document.getElementById("resultsSection").style.display = "block"

  // Update results display
  document.getElementById("scorePercentage").textContent = results.scorePercentage + "%"
  document.getElementById("correctAnswers").textContent = results.correctCount
  document.getElementById("totalQuestions").textContent = results.totalQuestions
  document.getElementById("timeTaken").textContent = formatTime(results.timeTaken)

  // Create review list
  const reviewList = document.getElementById("reviewList")
  reviewList.innerHTML = ""

  results.reviewItems.forEach((item) => {
    const reviewItem = document.createElement("div")
    reviewItem.className = `review-item ${item.isCorrect ? "correct" : "incorrect"}`

    reviewItem.innerHTML = `
      <div class="review-question">
        <strong>Q${item.questionNumber}:</strong> ${item.question}
      </div>
      <div class="review-answers">
        <div class="review-answer user-answer">
          <strong>Your answer:</strong> ${item.userAnswer}
        </div>
        <div class="review-answer correct-answer">
          <strong>Correct answer:</strong> ${item.correctAnswer}
        </div>
      </div>
    `

    reviewList.appendChild(reviewItem)
  })

  // Animate score circle
  animateScoreCircle(results.scorePercentage)
}

function animateScoreCircle(percentage) {
  const scoreCircle = document.querySelector(".score-circle")
  const scorePercentageElement = document.getElementById("scorePercentage")

  // Add animation class
  scoreCircle.classList.add("animate")

  // Animate percentage counter
  let currentPercentage = 0
  const increment = percentage / 50 // 50 steps for smooth animation

  const timer = setInterval(() => {
    currentPercentage += increment
    if (currentPercentage >= percentage) {
      currentPercentage = percentage
      clearInterval(timer)
    }
    scorePercentageElement.textContent = Math.round(currentPercentage) + "%"
  }, 20)
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`
}

// Navigation functions
function retakeQuiz() {
  // Reset quiz state
  currentQuestionIndex = 0
  userAnswers = new Array(currentQuiz.totalQuestions).fill(null)
  quizStartTime = new Date()

  // Show quiz section, hide results section
  document.getElementById("quizSection").style.display = "block"
  document.getElementById("resultsSection").style.display = "none"

  // Display first question
  displayQuestion()
}

function goToDashboard() {
  window.location.href = "dashboard.html"
}

function goToCategories() {
  window.location.href = "categories.html"
}