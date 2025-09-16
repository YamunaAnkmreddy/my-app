// Sample quiz questions database
const quizDatabase = {
  Science: {
    Physics: [
      {
        question: "What is the speed of light in vacuum?",
        options: ["299,792,458 m/s", "300,000,000 m/s", "186,000 miles/s", "3 × 10^8 m/s"],
        correct: 0,
        difficulty: "medium",
      },
      {
        question: "Which law states that force equals mass times acceleration?",
        options: ["Newton's First Law", "Newton's Second Law", "Newton's Third Law", "Law of Gravitation"],
        correct: 1,
        difficulty: "easy",
      },
      {
        question: "What is the unit of electric current?",
        options: ["Volt", "Watt", "Ampere", "Ohm"],
        correct: 2,
        difficulty: "easy",
      },
      {
        question: "What happens to the wavelength of light when it enters a denser medium?",
        options: ["Increases", "Decreases", "Stays the same", "Becomes zero"],
        correct: 1,
        difficulty: "hard",
      },
      {
        question: "Which particle has no electric charge?",
        options: ["Proton", "Electron", "Neutron", "Ion"],
        correct: 2,
        difficulty: "easy",
      },
    ],
    Chemistry: [
      {
        question: "What is the chemical symbol for gold?",
        options: ["Go", "Gd", "Au", "Ag"],
        correct: 2,
        difficulty: "easy",
      },
      {
        question: "How many electrons can the first shell of an atom hold?",
        options: ["2", "8", "18", "32"],
        correct: 0,
        difficulty: "medium",
      },
      {
        question: "What is the pH of pure water?",
        options: ["6", "7", "8", "9"],
        correct: 1,
        difficulty: "easy",
      },
      {
        question: "Which gas makes up approximately 78% of Earth's atmosphere?",
        options: ["Oxygen", "Carbon Dioxide", "Nitrogen", "Argon"],
        correct: 2,
        difficulty: "medium",
      },
      {
        question: "What type of bond forms between metals and non-metals?",
        options: ["Covalent", "Ionic", "Metallic", "Hydrogen"],
        correct: 1,
        difficulty: "medium",
      },
    ],
  },
  Mathematics: {
    Algebra: [
      {
        question: "What is the value of x in the equation 2x + 5 = 15?",
        options: ["5", "10", "7.5", "2.5"],
        correct: 0,
        difficulty: "easy",
      },
      {
        question: "What is the slope of the line y = 3x + 2?",
        options: ["2", "3", "5", "1"],
        correct: 1,
        difficulty: "easy",
      },
      {
        question: "If f(x) = x² + 3x + 2, what is f(2)?",
        options: ["8", "12", "10", "6"],
        correct: 1,
        difficulty: "medium",
      },
      {
        question: "What are the roots of x² - 5x + 6 = 0?",
        options: ["2 and 3", "1 and 6", "-2 and -3", "0 and 5"],
        correct: 0,
        difficulty: "medium",
      },
      {
        question: "What is the discriminant of ax² + bx + c = 0?",
        options: ["b² - 4ac", "b² + 4ac", "-b ± √(b² - 4ac)", "2a"],
        correct: 0,
        difficulty: "hard",
      },
    ],
    Geometry: [
      {
        question: "What is the sum of angles in a triangle?",
        options: ["90°", "180°", "270°", "360°"],
        correct: 1,
        difficulty: "easy",
      },
      {
        question: "What is the area of a circle with radius 5?",
        options: ["25π", "10π", "5π", "π"],
        correct: 0,
        difficulty: "medium",
      },
      {
        question: "How many sides does a hexagon have?",
        options: ["5", "6", "7", "8"],
        correct: 1,
        difficulty: "easy",
      },
      {
        question: "What is the Pythagorean theorem?",
        options: ["a + b = c", "a² + b² = c²", "a × b = c", "a/b = c"],
        correct: 1,
        difficulty: "easy",
      },
      {
        question: "What is the volume of a sphere with radius r?",
        options: ["πr²", "2πr", "4πr²", "(4/3)πr³"],
        correct: 3,
        difficulty: "hard",
      },
    ],
  },
  History: {
    "World History": [
      {
        question: "In which year did World War II end?",
        options: ["1944", "1945", "1946", "1947"],
        correct: 1,
        difficulty: "easy",
      },
      {
        question: "Who was the first person to walk on the moon?",
        options: ["Buzz Aldrin", "Neil Armstrong", "John Glenn", "Alan Shepard"],
        correct: 1,
        difficulty: "easy",
      },
      {
        question: "Which empire was ruled by Julius Caesar?",
        options: ["Greek Empire", "Roman Empire", "Byzantine Empire", "Ottoman Empire"],
        correct: 1,
        difficulty: "easy",
      },
      {
        question: "The Berlin Wall fell in which year?",
        options: ["1987", "1988", "1989", "1990"],
        correct: 2,
        difficulty: "medium",
      },
      {
        question: "Which ancient wonder of the world was located in Alexandria?",
        options: ["Hanging Gardens", "Colossus of Rhodes", "Lighthouse of Alexandria", "Statue of Zeus"],
        correct: 2,
        difficulty: "hard",
      },
    ],
  },
  Technology: {
    Programming: [
      {
        question: "Which of the following is not a programming language?",
        options: ["Python", "JavaScript", "HTML", "Java"],
        correct: 2,
        difficulty: "easy",
      },
      {
        question: "What does 'API' stand for?",
        options: [
          "Application Programming Interface",
          "Advanced Programming Integration",
          "Automated Program Instruction",
          "Application Process Integration",
        ],
        correct: 0,
        difficulty: "medium",
      },
      {
        question: "Which data structure follows LIFO principle?",
        options: ["Queue", "Stack", "Array", "Linked List"],
        correct: 1,
        difficulty: "medium",
      },
      {
        question: "What is the time complexity of binary search?",
        options: ["O(n)", "O(log n)", "O(n²)", "O(1)"],
        correct: 1,
        difficulty: "hard",
      },
      {
        question: "Which symbol is used for comments in Python?",
        options: ["//", "/*", "#", "<!--"],
        correct: 2,
        difficulty: "easy",
      },
    ],
  },
}

// Function to get questions for a specific category and subcategory
function getQuestions(category, subcategory, count = 10, difficulty = "all") {
  const categoryData = quizDatabase[category]
  if (!categoryData || !categoryData[subcategory]) {
    return []
  }

  let questions = [...categoryData[subcategory]]

  // Filter by difficulty if specified
  if (difficulty !== "all") {
    questions = questions.filter((q) => q.difficulty === difficulty)
  }

  // Shuffle questions
  questions = shuffleArray(questions)

  // Return requested number of questions
  return questions.slice(0, Math.min(count, questions.length))
}

// Utility function to shuffle array
function shuffleArray(array) {
  const shuffled = [...array]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}