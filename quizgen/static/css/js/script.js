// User data storage (in real app, this would be a database)
const users = JSON.parse(localStorage.getItem("quizUsers")) || []
let currentUser = JSON.parse(localStorage.getItem("currentUser")) || null
const quizHistory = JSON.parse(localStorage.getItem("quizHistory")) || []

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
  initializePage()
})

function initializePage() {
  const currentPage = window.location.pathname.split("/").pop() || "index.html"

  // Check authentication for protected pages
  if (currentPage !== "index.html" && currentPage !== "register.html" && !currentUser) {
    window.location.href = "index.html"
    return
  }

  // Initialize page-specific functionality
  switch (currentPage) {
    case "index.html":
      initializeLogin()
      break
    case "register.html":
      initializeRegister()
      break
    case "dashboard.html":
      initializeDashboard()
      break
  }
}

// Login functionality
function initializeLogin() {
  const loginForm = document.getElementById("loginForm")
  if (loginForm) {
    loginForm.addEventListener("submit", handleLogin)
  }
}

function handleLogin(e) {
  e.preventDefault()

  const email = document.getElementById("email").value
  const password = document.getElementById("password").value

  const user = users.find((u) => u.email === email && u.password === password)

  if (user) {
    currentUser = user
    localStorage.setItem("currentUser", JSON.stringify(currentUser))
    window.location.href = "dashboard.html"
  } else {
    alert("Invalid email or password")
  }
}

// Registration functionality
function initializeRegister() {
  const registerForm = document.getElementById("registerForm")
  if (registerForm) {
    registerForm.addEventListener("submit", handleRegister)
  }
}

function handleRegister(e) {
  e.preventDefault()

  const name = document.getElementById("name").value
  const email = document.getElementById("email").value
  const password = document.getElementById("password").value
  const confirmPassword = document.getElementById("confirmPassword").value

  // Validation
  if (password !== confirmPassword) {
    alert("Passwords do not match")
    return
  }

  if (users.find((u) => u.email === email)) {
    alert("Email already exists")
    return
  }

  // Create new user
  const newUser = {
    id: Date.now(),
    name: name,
    email: email,
    password: password,
    joinDate: new Date().toISOString(),
  }

  users.push(newUser)
  localStorage.setItem("quizUsers", JSON.stringify(users))

  alert("Account created successfully! Please login.")
  window.location.href = "index.html"
}

// Dashboard functionality
function initializeDashboard() {
  if (currentUser) {
    document.getElementById("userName").textContent = currentUser.name
    updateDashboardStats()
    drawPerformanceChart()
  }
}

function updateDashboardStats() {
  const userQuizzes = quizHistory.filter((quiz) => quiz.userId === currentUser.id)

  // Update stats
  document.getElementById("totalQuizzes").textContent = userQuizzes.length

  if (userQuizzes.length > 0) {
    const scores = userQuizzes.map((quiz) => quiz.score)
    const bestScore = Math.max(...scores)
    const averageScore = scores.reduce((a, b) => a + b, 0) / scores.length

    document.getElementById("bestScore").textContent = bestScore + "%"
    document.getElementById("averageScore").textContent = Math.round(averageScore) + "%"

    updateProgressBar("quizProgress", Math.min((userQuizzes.length / 10) * 100, 100))
    updateProgressBar("bestScoreProgress", bestScore)
    updateProgressBar("averageProgress", averageScore)

    // Update recent activity
    const recentQuizzes = userQuizzes.slice(-3).reverse()
    const activityList = document.getElementById("recentActivity")

    if (recentQuizzes.length > 0) {
      activityList.innerHTML = recentQuizzes
        .map(
          (quiz) =>
            `<div class="activity-item">
                    <strong>${quiz.category}</strong> - ${quiz.score}% 
                    <small>${new Date(quiz.date).toLocaleDateString()}</small>
                </div>`,
        )
        .join("")
    }
  } else {
    updateProgressBar("quizProgress", 0)
    updateProgressBar("bestScoreProgress", 0)
    updateProgressBar("averageProgress", 0)
  }
}

function updateProgressBar(elementId, percentage) {
  const progressBar = document.getElementById(elementId)
  if (progressBar) {
    setTimeout(() => {
      progressBar.style.width = percentage + "%"
    }, 100)
  }
}

function drawPerformanceChart() {
  const canvas = document.getElementById("performanceChart")
  if (!canvas) return

  const ctx = canvas.getContext("2d")
  const userQuizzes = quizHistory.filter((quiz) => quiz.userId === currentUser.id)

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height)

  if (userQuizzes.length === 0) {
    // Draw placeholder text
    ctx.fillStyle = "#64748b"
    ctx.font = "16px Arial"
    ctx.textAlign = "center"
    ctx.fillText("No quiz data yet. Take your first quiz!", canvas.width / 2, canvas.height / 2)
    return
  }

  // Get last 10 quizzes for the chart
  const recentQuizzes = userQuizzes.slice(-10)
  const scores = recentQuizzes.map((quiz) => quiz.score)

  // Chart dimensions
  const padding = 40
  const chartWidth = canvas.width - padding * 2
  const chartHeight = canvas.height - padding * 2

  // Draw axes
  ctx.strokeStyle = "#e5e7eb"
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.moveTo(padding, padding)
  ctx.lineTo(padding, canvas.height - padding)
  ctx.lineTo(canvas.width - padding, canvas.height - padding)
  ctx.stroke()

  // Draw grid lines
  ctx.strokeStyle = "#f1f5f9"
  ctx.lineWidth = 1
  for (let i = 1; i <= 4; i++) {
    const y = padding + (chartHeight / 4) * i
    ctx.beginPath()
    ctx.moveTo(padding, y)
    ctx.lineTo(canvas.width - padding, y)
    ctx.stroke()
  }

  // Draw score line
  if (scores.length > 1) {
    ctx.strokeStyle = "#2563eb"
    ctx.lineWidth = 3
    ctx.beginPath()

    scores.forEach((score, index) => {
      const x = padding + (chartWidth / (scores.length - 1)) * index
      const y = canvas.height - padding - (score / 100) * chartHeight

      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // Draw points
    ctx.fillStyle = "#2563eb"
    scores.forEach((score, index) => {
      const x = padding + (chartWidth / (scores.length - 1)) * index
      const y = canvas.height - padding - (score / 100) * chartHeight

      ctx.beginPath()
      ctx.arc(x, y, 4, 0, 2 * Math.PI)
      ctx.fill()
    })
  }

  // Draw labels
  ctx.fillStyle = "#64748b"
  ctx.font = "12px Arial"
  ctx.textAlign = "center"

  // Y-axis labels (scores)
  for (let i = 0; i <= 4; i++) {
    const score = (100 / 4) * i
    const y = canvas.height - padding - (chartHeight / 4) * i
    ctx.textAlign = "right"
    ctx.fillText(score + "%", padding - 10, y + 4)
  }

  // X-axis labels (quiz numbers)
  scores.forEach((score, index) => {
    const x = padding + (chartWidth / (scores.length - 1)) * index
    ctx.textAlign = "center"
    ctx.fillText(`Q${index + 1}`, x, canvas.height - padding + 20)
  })
}

// Logout functionality
function logout() {
  localStorage.removeItem("currentUser")
  currentUser = null
  window.location.href = "index.html"
}

function saveQuizResult(category, subcategory, score, totalQuestions) {
  const quizResult = {
    id: Date.now(),
    userId: currentUser.id,
    category: category,
    subcategory: subcategory,
    score: score,
    totalQuestions: totalQuestions,
    date: new Date().toISOString(),
  }

  const currentHistory = JSON.parse(localStorage.getItem("quizHistory")) || []
  currentHistory.push(quizResult)
  localStorage.setItem("quizHistory", JSON.stringify(currentHistory))
}