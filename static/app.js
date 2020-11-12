/**
 * Contains methods for the client side of the boggle webapp, and keeps track
 * of score.
 */
class Boggle {
  constructor() {
    this.score = 0;
    this.time = 60;
    this.timeout = false;
    this.wordsUsed = [];

    this.makeGuess = this.makeGuess.bind(this);
    this.decrementTimeByOne = this.decrementTimeByOne.bind(this);
  }

  /**
   * Validates input and makes a request to check if the word is a real word and
   * is in the board
   * @param {Object} event
   */
  async makeGuess(event) {
    event.preventDefault();
    const $guessInput = $("#guess-input");
    const guess = $guessInput.val().trim();
    $guessInput.val("");

    // check to make sure the game is in progress
    if (this.timeout) {
      return;
    }

    if (guess) {
      // check to make sure the word has not been used before
      if (this.wordsUsed.indexOf(guess) !== -1) {
        this.displayMessage("word-used");
      }
      else {
        const response = await axios.post("/guess", { guess });
        const result = response.data.result;
        this.displayMessage(result);
        this.updateWordsUsed(result, guess);
        this.updateScore(result);
      }
    }
    else {
      this.displayMessage("not-word");
    }
  }

  /**
   * Displays message to the user based on the validity of the user's guess
   * @param {string} messageCode Contains a code that describes the validity of
   * the user's guess
   */
  displayMessage(messageCode) {
    const $messageDiv = $("#message");

    /**
     * Handles displaying message in an alert with color based on category
     * @param {string} message 
     * @param {string} category 
     */
    function display(message, category) {
      $messageDiv.text(message);
      $messageDiv.removeClass();
      if (category === "success") {
        $messageDiv.addClass("alert alert-success");
      }
      else {
        $messageDiv.addClass("alert alert-danger");
      }
    }

    // decide based on validWord what message to display
    switch (messageCode) {
      case "ok":
        display("Correct", "success");
        break;
      case "not-on-board":
        display("That word is not on the board", "danger");
        break;
      case "not-word":
        display("That is not a valid word", "danger");
        break;
      case "word-used":
        display("You have already used that word", "danger");
        break;
    }
  }

  /**
   * Checks if messageCode is "ok", meaning the user typed in a valid word, and
   * if so, add word to list of words used
   * @param {string} messageCode Contains a code that describes the validity of
   * the user's guess
   * @param {string} word The word the user guessed for the game 
   */
  updateWordsUsed(messageCode, word) {
    if (messageCode === "ok") {
      this.wordsUsed.push(word);
    }
  }

  /**
   * Checks if messageCode is "ok", meaning the user typed in a valid word, and
   * if so, increments the score by 1
   * @param {string} messageCode Contains a code that describes the validity of
   * the user's guess
   */
  updateScore(messageCode) {
    if (messageCode === "ok") {
      this.score++;
      $("#score").text(`Score: ${this.score}`);
    }
  }

  /**
   * Starts a timer for the user to enter make guesses in the game. When the
   * time reaches 0, the game is stopped, and the user cannot make any more
   * guesses.
   */
  startTimer() {
    this.intervalId = setInterval(this.decrementTimeByOne, 1000);
  }

  /**
   * Decreases the time by 1, and if the time is 0, end the game and update the
   * HTML accordingly
   */
  async decrementTimeByOne() {
    this.time--;
    const $timeDiv = $("#time");
    
    if (this.time <= 0) {
      this.timeout = true;
      $timeDiv.text("You ran out of time. Game over!");
      $("#score").text(`Final score: ${this.score}`)
      $("#guess-form").hide();
      clearInterval(this.intervalId);
      await this.updateHighScoreAndGamesPlayed();
    }
    else {
      $timeDiv.text(`You have ${this.time} seconds left!`);
    }
  }

  /**
   * Makes a request to update the user's highest score and the number of times
   * the user has played the game. Then updates the
   * webpage and to reflect the new stats.
   */
  async updateHighScoreAndGamesPlayed() {
    const response = await axios.post("/stats", { "score": this.score });
    const numOfTimesPlayed = response.data.num_of_times_played;
    const highscore = response.data.highscore;
    $("#highscore").text(`Your highest score: ${highscore}`);
    $("#times-played").text(`You have played ${numOfTimesPlayed} times`);
  }
}

const boggle = new Boggle();
boggle.startTimer();
$("#guess-form").on("submit", boggle.makeGuess);