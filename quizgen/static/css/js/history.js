// History page functionality
let allHistory = []
let filteredHistory = []
const currentUser = { id: 1 } // Declare currentUser variable for demonstration purposes

// Initialize history page
document.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname.includes("history.html")) {
    initializeHistory()
  }
})

function initializeHistory() {
  loadHistoryData()
  populateCategoryFilter()
  updateHistoryStats()
  displayHistory()
}

function loadHistoryData() {
  const quizHistory = JSON.parse(localStorage.getItem("quizHistory")) || []
  allHistory = quizHistory.filter((quiz) => quiz.userId === currentUser.id)
  filteredHistory = [...allHistory]
}

function populateCategoryFilter() {
  const categoryFilter = document.getElementById("categoryFilter")
  const categories = [...new Set(allHistory.map((quiz) => quiz.category))]

  // Clear existing options except "All Categories"
  categoryFilter.innerHTML = '<option value="all">All Categories</option>'

  categories.forEach((category) => {
    const option = document.createElement("option")
    option.value = category
    option.textContent = category
    categoryFilter.appendChild(option)
  })
}

function updateHistoryStats() {
  const totalQuizzes = allHistory.length
  document.getElementById("totalHistoryQuizzes").textContent = totalQuizzes

  if (totalQuizzes === 0) {
    document.getElementById("historyAverageScore").textContent = "0%"
    document.getElementById("bestCategory").textContent = "-"
    document.getElementById("improvement").textContent = "0%"
    return
  }

  // Calculate average score
  const averageScore = allHistory.reduce((sum, quiz) => sum + quiz.score, 0) / totalQuizzes
  document.getElementById("historyAverageScore").textContent = Math.round(averageScore) + "%"

  // Find best category
  const categoryScores = {}
  allHistory.forEach((quiz) => {
    if (!categoryScores[quiz.category]) {
      categoryScores[quiz.category] = []
    }
    categoryScores[quiz.category].push(quiz.score)
  })

  let bestCategory = "-"
  let bestAverage = 0

  Object.keys(categoryScores).forEach((category) => {
    const average = categoryScores[category].reduce((sum, score) => sum + score, 0) / categoryScores[category].length
    if (average > bestAverage) {
      bestAverage = average
      bestCategory = category
    }
  })

  document.getElementById("bestCategory").textContent = bestCategory

  // Calculate improvement (compare first 3 quizzes with last 3)
  if (totalQuizzes >= 6) {
    const firstThree = allHistory.slice(0, 3)
    const lastThree = allHistory.slice(-3)

    const firstAverage = firstThree.reduce((sum, quiz) => sum + quiz.score, 0) / 3
    const lastAverage = lastThree.reduce((sum, quiz) => sum + quiz.score, 0) / 3

    const improvement = lastAverage - firstAverage
    const improvementText = improvement > 0 ? `+${Math.round(improvement)}%` : `${Math.round(improvement)}%`
    document.getElementById("improvement").textContent = improvementText
  } else {
    document.getElementById("improvement").textContent = "N/A"
  }
}

function displayHistory() {
  const historyList = document.getElementById("historyList")
  const noHistory = document.getElementById("noHistory")

  if (filteredHistory.length === 0) {
    historyList.style.display = "none"
    noHistory.style.display = "block"
    return
  }

  historyList.style.display = "block"
  noHistory.style.display = "none"

  historyList.innerHTML = ""

  filteredHistory.forEach((quiz) => {
    const historyItem = createHistoryItem(quiz)
    historyList.appendChild(historyItem)
  })
}

function createHistoryItem(quiz) {
  const item = document.createElement("div")
  item.className = "history-item"

  const scoreClass = getScoreClass(quiz.score)
  const date = new Date(quiz.date).toLocaleDateString()
  const time = new Date(quiz.date).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })

  item.innerHTML = `
    <div class="history-item-header">
      <div class="quiz-info">
        <h4>${quiz.category}</h4>
        <p>${quiz.subcategory}</p>
      </div>
      <div class="quiz-score ${scoreClass}">
        <span class="score-value">${quiz.score}%</span>
        <span class="score-label">Score</span>
      </div>
    </div>
    <div class="history-item-details">
      <div class="detail-item">
        <span class="detail-label">Date:</span>
        <span class="detail-value">${date}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Time:</span>
        <span class="detail-value">${time}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Questions:</span>
        <span class="detail-value">${quiz.totalQuestions}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Correct:</span>
        <span class="detail-value">${Math.round((quiz.score / 100) * quiz.totalQuestions)}</span>
      </div>
    </div>
    <div class="history-item-actions">
      <button class="btn btn-secondary btn-small" onclick="retakeQuiz('${quiz.category}', '${quiz.subcategory}')">
        Retake Quiz
      </button>
    </div>
  `

  return item
}

function getScoreClass(score) {
  if (score >= 90) return "excellent"
  if (score >= 80) return "good"
  if (score >= 70) return "average"
  if (score >= 60) return "below-average"
  return "poor"
}

function filterHistory() {
  const categoryFilter = document.getElementById("categoryFilter")
  const selectedCategory = categoryFilter.value

  if (selectedCategory === "all") {
    filteredHistory = [...allHistory]
  } else {
    filteredHistory = allHistory.filter((quiz) => quiz.category === selectedCategory)
  }

  sortHistory()
  displayHistory()
}

function sortHistory() {
  const sortBy = document.getElementById("sortBy").value

  filteredHistory.sort((a, b) => {
    switch (sortBy) {
      case "date-desc":
        return new Date(b.date) - new Date(a.date)
      case "date-asc":
        return new Date(a.date) - new Date(b.date)
      case "score-desc":
        return b.score - a.score
      case "score-asc":
        return a.score - b.score
      default:
        return new Date(b.date) - new Date(a.date)
    }
  })

  displayHistory()
}

function retakeQuiz(category, subcategory) {
  // Set quiz settings and navigate to categories page
  const quizSettings = {
    category: category,
    subcategory: subcategory,
    questionCount: 10,
    difficulty: "medium",
  }

  sessionStorage.setItem("currentQuizSettings", JSON.stringify(quizSettings))
  window.location.href = "quiz.html"
}