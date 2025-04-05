document.getElementById("taskName").addEventListener("input", function () {
  let maxLength = 30;
  let charCount = this.value.length;
  
  if (charCount > maxLength) {
      this.value = this.value.slice(0, maxLength);
  }

  document.getElementById("charCount").textContent = `${this.value.length}/30 characters`;
});



document.getElementById('createTaskButton').addEventListener('click', function() {
  var taskName = document.getElementById('taskName').value;
  var taskColor = document.getElementById('taskColor').value;

  if (taskName === "") {
    showToast('error', 'Please, provide a task name');
    return;
  }

  if (taskColor === "") {
    showToast('error', 'Please, select a task color');
    return;
  }

  fetch("/task/new_task", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ name: taskName, color: taskColor })
  })
  .then(response => response.json())
  .then(({ success, message, data, error }) => {
    if (success){
      var taskHTML = `
        <div class="col-md-4">
          <div 
            class="d-flex custom-card " 
            style="border-color : ${data.color}"
            data-id="${data.id}"> 

            <div class="flex-grow-1">
              <h3 class="text-break">${data.name}</h3>
              <p>Today: ${data.today_total_time}</p>
              <p>Week: ${data.week_total_time}</p>
            </div>

            <div class="flex-shrink-0">
              <canvas id="myPieChart-${data.id}" style="max-width: 150px; max-height: 150px;"></canvas>
            </div>

          </div>
        </div>
      `;
      document.querySelector('#taskGrid').innerHTML += taskHTML;
      $('#newTask').modal('hide'); 
      reinitializateChartContentAfterDOMUpdate();
      showToast('success', message);
    } else {
      showToast('error', message || 'Erro ao criar a Task');
      console.log(error)
    }
  })
  .catch((error) => {
    showToast('error', 'Something went wrong while creating a task. Please try again later.');
    console.error("Erro ao criar Task: ", error);
  }); 
});