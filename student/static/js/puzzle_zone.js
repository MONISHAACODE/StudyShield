
document.addEventListener("DOMContentLoaded", function () {
    // HTML elements
    const gamePanel = document.getElementById("gamePanel");
    const gameBoard = document.getElementById("gameBoard");
    const gameTitle = document.getElementById("gameTitle");
    const gameMessage = document.getElementById("gameMessage");
    const gameTimer = document.getElementById("gameTimer");
    const difficulty = document.getElementById("difficulty");
    const closeGame = document.getElementById("closeGame");
    const restartGame = document.getElementById("restartGame");
    const themeToggle = document.getElementById("themeToggle");

    const gameButtons = document.querySelectorAll("[data-game]");

    let currentGame = "";
    let timerInterval = null;
    let seconds = 0;
    let memoryFirstCard = null;
    let memoryLocked = false;
    let memoryMatches = 0;

    // Theme
    const savedTheme = localStorage.getItem("studyShieldTheme");

    if (savedTheme === "light") {
        document.documentElement.classList.add("light-theme");
    } else {
        document.documentElement.classList.remove("light-theme");
    }

    if (themeToggle) {
        themeToggle.addEventListener("click", function () {
            document.documentElement.classList.toggle("light-theme");

            const isLight = document.documentElement.classList.contains("light-theme");
            localStorage.setItem(
                "studyShieldTheme",
                isLight ? "light" : "dark"
            );
        });
    }

    // Common helpers
    function stopTimer() {
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }

    function startTimer() {
        stopTimer();
        seconds = 0;
        updateTimer();

        timerInterval = setInterval(function () {
            seconds++;
            updateTimer();
        }, 1000);
    }

    function updateTimer() {
        if (!gameTimer) return;

        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;

        gameTimer.textContent =
            String(minutes).padStart(2, "0") +
            ":" +
            String(remainingSeconds).padStart(2, "0");
    }

    function showMessage(message) {
        if (gameMessage) {
            gameMessage.textContent = message;
        }
    }

    function addButton(text, callback) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = text;
        button.addEventListener("click", callback);
        return button;
    }

    function addInput(placeholder, type = "text") {
        const input = document.createElement("input");
        input.type = type;
        input.placeholder = placeholder;
        input.autocomplete = "off";
        input.style.padding = "10px";
        input.style.margin = "8px";
        input.style.maxWidth = "100%";
        return input;
    }

    function prepareGame(title) {
        if (!gamePanel || !gameBoard) {
            console.error(
                "Game elements missing. Check puzzle_zone.html IDs."
            );
            return false;
        }

        gamePanel.hidden = false;
        gamePanel.style.display = "block";
        gameBoard.replaceChildren();

        if (gameTitle) {
            gameTitle.textContent = title;
        }

        showMessage("Game started! Good luck!");
        startTimer();

        gamePanel.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        return true;
    }

    function getDifficulty() {
        return difficulty ? difficulty.value : "easy";
    }

    // Open selected game
    gameButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            currentGame = button.dataset.game;

            if (currentGame === "number") {
                showNumberPuzzle();
            } else if (currentGame === "word") {
                showWordPuzzle();
            } else if (currentGame === "logic") {
                showLogicPuzzle();
            } else if (currentGame === "memory") {
                showMemoryGame();
            } else {
                console.error("Unknown game:", currentGame);
            }
        });
    });

    // 1. Number Quest
    function showNumberPuzzle() {
        if (!prepareGame("Number Quest")) return;

        const level = getDifficulty();
        let answer;

        if (level === "hard") {
            answer = Math.floor(Math.random() * 900) + 100;
        } else if (level === "medium") {
            answer = Math.floor(Math.random() * 90) + 10;
        } else {
            answer = Math.floor(Math.random() * 10) + 1;
        }

        const question = document.createElement("p");
        question.textContent =
            "Guess the secret number! " +
            (level === "easy" ? "Choose 1–10." :
            level === "medium" ? "Choose 10–99." : "Choose 100–999.");

        const input = addInput("Enter your guess", "number");
        input.min = level === "easy" ? "1" : level === "medium" ? "10" : "100";
        input.max = level === "easy" ? "10" : level === "medium" ? "99" : "999";

        const checkButton = addButton("Check Answer", checkAnswer);
        const attemptsText = document.createElement("p");
        let attempts = 0;

        function checkAnswer() {
            const guess = Number(input.value);

            if (!input.value.trim() || !Number.isFinite(guess)) {
                showMessage("Please enter a valid number.");
                return;
            }

            attempts++;

            if (guess === answer) {
                showMessage("Correct! You solved it in " + attempts + " attempt(s). 🎉");
                stopTimer();
                checkButton.disabled = true;
            } else if (guess < answer) {
                showMessage("Too low! Try a bigger number.");
            } else {
                showMessage("Too high! Try a smaller number.");
            }

            attemptsText.textContent = "Attempts: " + attempts;
            input.value = "";
            input.focus();
        }

        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter") checkAnswer();
        });

        gameBoard.append(question, input, checkButton, attemptsText);
        input.focus();
    }

    // 2. Word Scramble
    function showWordPuzzle() {
        if (!prepareGame("Word Scramble")) return;

        const words = [
            { word: "PYTHON", hint: "A popular programming language" },
            { word: "BROWSER", hint: "Used to access websites" },
            { word: "PUZZLE", hint: "A game that tests your thinking" },
            { word: "CODING", hint: "Writing instructions for a computer" },
            { word: "LOGIC", hint: "Reasoning and problem solving" },
            { word: "COMPUTER", hint: "An electronic computing device" }
        ];

        const item = words[Math.floor(Math.random() * words.length)];
        const scrambled = item.word
            .split("")
            .sort(() => Math.random() - 0.5)
            .join("");

        const scrambledText = document.createElement("h3");
        scrambledText.textContent = scrambled;

        const hint = document.createElement("p");
        hint.textContent = "Hint: " + item.hint;

        const input = addInput("Enter the correct word");
        const checkButton = addButton("Check Word", checkWord);

        function checkWord() {
            if (input.value.trim().toUpperCase() === item.word) {
                showMessage("Correct word! Well done! 🎉");
                stopTimer();
                checkButton.disabled = true;
            } else {
                showMessage("Not quite! Try again.");
            }
        }

        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter") checkWord();
        });

        gameBoard.append(scrambledText, hint, input, checkButton);
        input.focus();
    }

    // 3. Logic Puzzle
    function showLogicPuzzle() {
        if (!prepareGame("Logic Puzzle")) return;

        const level = getDifficulty();
        let question;
        let answer;
        let explanation;

        if (level === "easy") {
            question = "What comes next? 2, 4, 6, 8, ?";
            answer = "10";
            explanation = "Each number increases by 2.";
        } else if (level === "medium") {
            question = "What comes next? 3, 6, 12, 24, ?";
            answer = "48";
            explanation = "Each number is multiplied by 2.";
        } else {
            question = "What comes next? 1, 4, 9, 16, 25, ?";
            answer = "36";
            explanation = "These are square numbers: 1², 2², 3², and so on.";
        }

        const questionText = document.createElement("h3");
        questionText.textContent = question;

        const input = addInput("Your answer", "number");
        const checkButton = addButton("Submit Answer", checkAnswer);

        function checkAnswer() {
            if (input.value.trim() === answer) {
                showMessage("Correct! " + explanation + " 🎉");
                stopTimer();
                checkButton.disabled = true;
            } else {
                showMessage("Incorrect. Think about the pattern and try again.");
            }
        }

        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter") checkAnswer();
        });

        gameBoard.append(questionText, input, checkButton);
        input.focus();
    }

    // 4. Memory Match
    function showMemoryGame() {
        if (!prepareGame("Memory Match")) return;

        memoryFirstCard = null;
        memoryLocked = false;
        memoryMatches = 0;

        const symbols = ["🌸", "🌙", "⭐", "🍀"];
        const cards = [...symbols, ...symbols].sort(
            () => Math.random() - 0.5
        );

        const instructions = document.createElement("p");
        instructions.textContent = "Find all matching pairs.";

        const grid = document.createElement("div");
        grid.style.display = "grid";
        grid.style.gridTemplateColumns = "repeat(4, minmax(45px, 1fr))";
        grid.style.gap = "10px";
        grid.style.maxWidth = "360px";
        grid.style.margin = "16px auto";

        cards.forEach(function (symbol, index) {
            const card = addButton("?", function () {
                flipCard(card, symbol);
            });

            card.dataset.index = String(index);
            card.dataset.symbol = symbol;
            card.style.fontSize = "24px";
            card.style.minHeight = "60px";
            card.style.cursor = "pointer";

            grid.appendChild(card);
        });

        const matchesText = document.createElement("p");
        matchesText.textContent = "Pairs found: 0 / " + symbols.length;

        gameBoard.append(instructions, grid, matchesText);

        function flipCard(card, symbol) {
            if (
                memoryLocked ||
                card.dataset.matched === "true" ||
                card === memoryFirstCard ||
                card.textContent !== "?"
            ) {
                return;
            }

            card.textContent = symbol;

            if (!memoryFirstCard) {
                memoryFirstCard = card;
                return;
            }

            if (memoryFirstCard.dataset.symbol === symbol) {
                memoryFirstCard.dataset.matched = "true";
                card.dataset.matched = "true";
                memoryFirstCard.disabled = true;
                card.disabled = true;

                memoryFirstCard = null;
                memoryMatches++;
                matchesText.textContent =
                    "Pairs found: " + memoryMatches + " / " + symbols.length;

                if (memoryMatches === symbols.length) {
                    showMessage("Amazing! You found every pair! 🎉");
                    stopTimer();
                }
            } else {
                memoryLocked = true;
                const firstCard = memoryFirstCard;
                memoryFirstCard = null;

                setTimeout(function () {
                    firstCard.textContent = "?";
                    card.textContent = "?";
                    memoryLocked = false;
                }, 800);
            }
        }
    }

    // Close current game
    if (closeGame) {
        closeGame.addEventListener("click", function () {
            stopTimer();

            if (gamePanel) {
                gamePanel.hidden = true;
                gamePanel.style.display = "";
            }

            if (gameBoard) {
                gameBoard.replaceChildren();
            }

            currentGame = "";
            showMessage("");
        });
    }

    // Restart current game
    if (restartGame) {
        restartGame.addEventListener("click", function () {
            if (currentGame === "number") {
                showNumberPuzzle();
            } else if (currentGame === "word") {
                showWordPuzzle();
            } else if (currentGame === "logic") {
                showLogicPuzzle();
            } else if (currentGame === "memory") {
                showMemoryGame();
            }
        });
    }
});
