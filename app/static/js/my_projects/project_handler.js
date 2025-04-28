document.getElementById("projectTitle").addEventListener("input", function () {
  let maxLength = 30;
  let charCount = this.value.length;
  
  if (charCount > maxLength) {
      this.value = this.value.slice(0, maxLength);
  }

  document.getElementById("charCount").textContent = `${this.value.length}/30 characters`;
});


document.getElementById('createProjectButton').addEventListener('click', function() {
  var projectTitle = document.getElementById('projectTitle').value;
  var projectColor = document.getElementById('projectColor').value;

  if (projectTitle === "") {
    showToast('error', 'Please, provide a project title');
    return;
  }

  if (projectColor === "") {
    showToast('error', 'Please, select a project color');
    return;
  }

  const createProjectButton = document.getElementById('createProjectButton');
  createProjectButton.disabled = true;

  fetch("/project/create_project", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ title: projectTitle, color: projectColor })
  })
  .then(response => response.json())
  .then(({ success, message, data, error }) => {
    if (success){
        var taskHTML = `
          <div class="col-sm-12 col-md-6 col-lg-4">
              <div 
                class="d-flex custom-card " 
                style="border-color : ${data.color}"
                data-id="${data.identificator}"> 

                <div class="flex-grow-1">
                  <h3 class="text-break">${data.title}</h3>
                  <p>Today: ${data.today_total_time || '00h00m'}</p>
                  <p>Week: ${data.week_total_time || '00h00m'}</p>
                </div>

                <div class="flex-shrink-0">
                  <canvas id="myPieChart-${data.identificator}" style="max-width: 150px; max-height: 150px;"></canvas>
                </div>

              </div>
            </div>
          `;
      allProjectsData.push(data);
      document.querySelector('#projectGrid').innerHTML += taskHTML;
      $('#newProject').modal('hide'); 
      inicializateChartContent();
      showToast('success', message);
    } else {
      showToast('error', message || 'Erro ao criar project');
      console.log(error)
    }
  })
  .catch((error) => {
    showToast('error', 'Something went wrong while creating a task. Please try again later.');
    console.error("Erro ao criar Task: ", error);
  }).finally(() => {
    createProjectButton.disabled = false;
  });
});
