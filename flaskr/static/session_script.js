class Timer {
    constructor(root) {
      this.root = root;
      root.innerHTML = Timer.getHTML();

      this.work_done_audio = document.getElementById('work-done-audio');
      this.rest_done_audio = document.getElementById('rest-done-audio');
      
      
      this.el = {
        minutes: root.querySelector(".timer__part--minutes"),
        seconds: root.querySelector(".timer__part--seconds"),
        control: root.querySelector(".timer__btn--control"),
        reset: root.querySelector(".timer__btn--reset"),
        restControl: root.querySelector(".timer__btn--rest-control"),
        label: root.querySelector(".timer-label")
      };
  
      this.interval = null;
      this.remainingSeconds = 1800;
      this.working = true;
      this.updateInterfaceTime();
  
      this.el.control.addEventListener("click", () => {
        if (this.interval === null) {
          this.start();
        } else {
          this.stop();
        }
      });
  
      this.el.reset.addEventListener("click", () => {
        const input = prompt("Enter number of minutes:");

        if (!input) return;

        const inputMinutes = parseFloat(input).toFixed(1);

        if (inputMinutes <= 999 && inputMinutes > 0) {
          this.remainingSeconds = inputMinutes * 60;
          this.updateInterfaceTime();
        }
        else {
            alert("You must enter a valid number between 0 and 999.")
        }
      });

      this.el.restControl.addEventListener("click", () => {
        if (this.working) {
            this.remainingSeconds = 600;
            this.rest()
            this.updateInterfaceTime()
        } else {
            this.work()
            this.updateInterfaceTime()
        }
      });
    }
  
    updateInterfaceTime() {
      const minutes = Math.floor(this.remainingSeconds / 60);
      const seconds = this.remainingSeconds % 60;
  
      this.el.minutes.textContent = minutes.toString().padStart(2, "0");
      this.el.seconds.textContent = seconds.toString().padStart(2, "0");
    }
  
    updateInterfaceControls() {
      if (this.interval === null) {
        this.el.control.innerHTML = `<span class="material-symbols-outlined">play_arrow</span>`;
        this.el.control.classList.add("timer__btn--start");
        this.el.control.classList.remove("timer__btn--stop");
      } else {
        this.el.control.innerHTML = `<span class="material-symbols-outlined">pause</span>`;
        this.el.control.classList.add("timer__btn--stop");
        this.el.control.classList.remove("timer__btn--start");
      }

      if (this.working === !true) {
        this.el.restControl.innerHTML = `<span class="material-symbols-outlined">book_5</span>`;
        this.el.control.classList.add("timer__btn--work");
        this.el.control.classList.remove("timer__btn--rest");
        this.el.label.innerHTML = "Break Time!";
      } else {
        this.el.restControl.innerHTML = `<span class="material-symbols-outlined">self_improvement</span>`;
        this.el.control.classList.add("timer__btn--rest");
        this.el.control.classList.remove("timer__btn--work");
        this.el.label.innerHTML = "Work Time!";
      }
    }
  
    start() {
      if (this.remainingSeconds === 0) return;
  
      this.interval = setInterval(() => {
      this.remainingSeconds--;
      this.updateInterfaceTime();
    //   document.body.background = "red";
  
        if (this.remainingSeconds === 0) {
            if (this.working) {
                this.work_done_audio.play();
                
            }
            else {
                this.rest_done_audio.play();
            }
          this.stop();
          this.work();
          this.updateInterfaceTime();
        }
      }, 1000);
  
      this.updateInterfaceControls();
    }
  
    stop() {
      clearInterval(this.interval);
  
      this.interval = null;
  
      this.updateInterfaceControls();
    }

    rest() {
        this.working = false;
        this.root.style.background = "#c19af5";
        this.stop()
        this.start()
        this.updateInterfaceControls();
    }

    work() {
        this.working = true;
        this.root.style.background = "white";
        this.updateInterfaceControls();
    }
  
    static getHTML() {
      return `
              <div class="timer-label">Work Time!</div>
              <span class="timer__part timer__part--minutes">00</span>
              <span class="timer__part">:</span>
              <span class="timer__part timer__part--seconds">00</span>
              <div class="timer__buttons">
                <button type="button" class="timer__btn timer__btn--control timer__btn--start">
                    <span class="material-symbols-outlined">play_arrow</span>
                </button>
                <button type="button" class="timer__btn timer__btn--reset">
                    <span class="material-symbols-outlined">timer</span>
                </button>
                <button type="button" class="timer__btn timer__btn--rest-control timer__btn--rest">
                    <span class="material-symbols-outlined">self_improvement</span>
                </button>
              </div>
          `;
    }
  }
  

document.addEventListener("DOMContentLoaded", () => {
    new Timer(
        document.querySelector(".timer")
    );
});

