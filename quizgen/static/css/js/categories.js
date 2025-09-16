// Quiz categories and subcategories data
const quizCategories = {
  Science: {
    icon: "🔬",
    subcategories: ["Physics", "Chemistry", "Biology", "Earth Science", "Astronomy"],
  },
  Mathematics: {
    icon: "📊",
    subcategories: ["Algebra", "Geometry", "Calculus", "Statistics", "Number Theory"],
  },
  History: {
    icon: "📚",
    subcategories: ["World History", "American History", "Ancient History", "Modern History", "Military History"],
  },
  Geography: {
    icon: "🌍",
    subcategories: ["World Geography", "Physical Geography", "Political Geography", "Climate", "Capitals"],
  },
  Literature: {
    icon: "📖",
    subcategories: ["Classic Literature", "Modern Literature", "Poetry", "Drama", "World Literature"],
  },
  Technology: {
    icon: "💻",
    subcategories: ["Programming", "Web Development", "Artificial Intelligence", "Cybersecurity", "Mobile Development"],
  },
  Sports: {
    icon: "⚽",
    subcategories: ["Football", "Basketball", "Baseball", "Soccer", "Olympics"],
  },
  Entertainment: {
    icon: "🎬",
    subcategories: ["Movies", "Music", "TV Shows", "Video Games", "Celebrities"],
  },
}

let selectedCategory = null
let selectedSubcategory = null

// Initialize categories page
document.addEventListener("DOMContentLoaded", () => {
  if (window.location.pathname.includes("categories.html")) {
    initializeCategories()
  }
})

function initializeCategories() {
  renderCategories()
}

function renderCategories() {
  const categoryGrid = document.getElementById("categoryGrid")
  categoryGrid.innerHTML = ""

  Object.keys(quizCategories).forEach((category) => {
    const categoryCard = document.createElement("div")
    categoryCard.className = "category-card"
    categoryCard.onclick = () => selectCategory(category)

    categoryCard.innerHTML = `
      <div class="category-icon">${quizCategories[category].icon}</div>
      <h4>${category}</h4>
      <p>${quizCategories[category].subcategories.length} topics</p>
    `

    categoryGrid.appendChild(categoryCard)
  })
}

function selectCategory(category) {
  selectedCategory = category
  selectedSubcategory = null

  // Update UI
  updateCategorySelection()
  renderSubcategories(category)
  showStep("subcategoryStep")
  hideStep("quizSettings")
  hideStep("actionSection")
  hideStep("selectedInfo")
}

function updateCategorySelection() {
  // Remove previous selections
  document.querySelectorAll(".category-card").forEach((card) => {
    card.classList.remove("selected")
  })

  // Add selection to current category
  const categoryCards = document.querySelectorAll(".category-card")
  categoryCards.forEach((card) => {
    if (card.querySelector("h4").textContent === selectedCategory) {
      card.classList.add("selected")
    }
  })
}

function renderSubcategories(category) {
  const subcategoryGrid = document.getElementById("subcategoryGrid")
  subcategoryGrid.innerHTML = ""

  quizCategories[category].subcategories.forEach((subcategory) => {
    const subcategoryCard = document.createElement("div")
    subcategoryCard.className = "subcategory-card"
    subcategoryCard.onclick = () => selectSubcategory(subcategory)

    subcategoryCard.innerHTML = `
      <h5>${subcategory}</h5>
    `

    subcategoryGrid.appendChild(subcategoryCard)
  })
}

function selectSubcategory(subcategory) {
  selectedSubcategory = subcategory

  // Update UI
  updateSubcategorySelection()
  showStep("quizSettings")
  showStep("actionSection")
  updateSelectedInfo()
}

function updateSubcategorySelection() {
  // Remove previous selections
  document.querySelectorAll(".subcategory-card").forEach((card) => {
    card.classList.remove("selected")
  })

  // Add selection to current subcategory
  const subcategoryCards = document.querySelectorAll(".subcategory-card")
  subcategoryCards.forEach((card) => {
    if (card.querySelector("h5").textContent === selectedSubcategory) {
      card.classList.add("selected")
    }
  })
}

function updateSelectedInfo() {
  document.getElementById("selectedCategory").textContent = selectedCategory
  document.getElementById("selectedSubcategory").textContent = selectedSubcategory
  showStep("selectedInfo")
}

function showStep(stepId) {
  document.getElementById(stepId).style.display = "block"
}

function hideStep(stepId) {
  document.getElementById(stepId).style.display = "none"
}

function resetSelection() {
  selectedCategory = null
  selectedSubcategory = null

  // Reset UI
  document.querySelectorAll(".category-card, .subcategory-card").forEach((card) => {
    card.classList.remove("selected")
  })

  hideStep("subcategoryStep")
  hideStep("quizSettings")
  hideStep("actionSection")
  hideStep("selectedInfo")
}

function startQuiz() {
  if (!selectedCategory || !selectedSubcategory) {
    alert("Please select both category and subcategory")
    return
  }

  const questionCount = document.getElementById("questionCount").value
  const difficulty = document.getElementById("difficulty").value

  // Store quiz settings in sessionStorage
  const quizSettings = {
    category: selectedCategory,
    subcategory: selectedSubcategory,
    questionCount: Number.parseInt(questionCount),
    difficulty: difficulty,
  }

  sessionStorage.setItem("currentQuizSettings", JSON.stringify(quizSettings))

  // Navigate to quiz page
  window.location.href = "quiz.html"
}