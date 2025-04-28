// Mudar aqui, o problema e q o global desse arquivo e do timer.js estao sendo compartilhados, isso nao pode acontecer (ou pode? tem que ver se uso isso em algum lugar)
//projectID = project_data.project_id; 

document.getElementById('createTaskButton').addEventListener('click', function() {
  const taskTitle = document.getElementById('taskTitle').value.trim();

  if (taskTitle === "") {
      showToast('error', 'Please, provide a task title');
      return;
  }

  fetch(`/task/${projectID}/create_task`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: taskTitle })
  })
  .then(response => response.json())
  .then(({ success, message, data, error }) => {
      if (success) {
          const formattedCreatedTime = formatDate(data.created_at);
          const taskHTML = `
              <div class="col-md-12 task-item">
                  <div class="d-flex justify-content-between align-items-center task-card" data-id="${data.id}">
                      <div class="task-text-check d-flex align-items-center">
                          <input class="form-check-input task-check-box me-3 mt-0 rounded-checkbox" type="checkbox" aria-label="...">
                          <span class="task-title mb-0">${data.title}</span>
                      </div>
                      <div class="icons">
                          <i class="bi bi-info-circle fs-4 me-3" id="infoTask" data-bs-toggle="tooltip" data-bs-placement="left"
                              data-bs-custom-class="info-task-tooltip" data-bs-html="true" title="Created Time:<br>${formattedCreatedTime}">
                          </i>
                          <i class="bi bi-trash fs-4" id="deleteTaskButton" data-bs-toggle="modal" data-bs-target="#deleteTaskModal"></i>
                      </div>
                  </div>
              </div>`;
          document.querySelector('#taskGridInProgress').innerHTML += taskHTML;
          $('#newTask').modal('hide');
          showToast('success', message);
          reinitializateTaskTooltipsAfterDOMUpdate();
      } else {
          showToast('error', message || 'Erro ao criar a Task.');
      }
  })
  .catch(() => showToast('error', 'Something went wrong. Please try again later.'));
});

// Change State REFATORAR ESSA PARTE AQUI, TA MUITO CONFUSO

document.querySelectorAll('.task-grid').forEach(grid => {
  grid.addEventListener('click', function (event) {
    const checkbox = event.target.closest('.task-check-box');
    if (checkbox) {
      const taskCard = checkbox.closest('.task-card');
      const taskItem = checkbox.closest('.task-item');
      if (taskCard) {
        const taskID = taskCard.getAttribute('data-id');
        const isChecked = checkbox.checked;

        fetch(`/task/${projectID}/change_status/${taskID}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ status: isChecked ? "completed" : "in progress" }),
        })
          .then(response => response.json())
          .then(({ success, message, data, error })  => {
            if (success) {
              const infoIcon = taskItem.querySelector('#infoTask');

              const currentGrid = isChecked
                ? document.querySelector('#taskGridInProgress')
                : document.querySelector('#taskGridCompleted');
              const newGrid = isChecked
                ? document.querySelector('#taskGridCompleted')
                : document.querySelector('#taskGridInProgress');

              currentGrid.removeChild(taskItem);
            
              const taskTitle = taskItem.querySelector('.task-title');
              if (taskTitle) {
                taskTitle.innerHTML = isChecked
                  ? `<del>${taskTitle.textContent}</del>`
                  : taskTitle.textContent.replace(/<del>|<\/del>/g, "");
              }
              
              if (infoIcon) {
                const formattedCreatedTime = formatDate(data.created_at);
                let newTitle = `Created Time:<br>${formattedCreatedTime}`; 

                if (data.status == 'completed') {
                  const formattedCompletedTime = formatDate(data.completed_at);
                  newTitle += `<br>Completed Time:<br>${formattedCompletedTime}`;
                }

                infoIcon.setAttribute('title', newTitle);
              }
                 
              
              newGrid.appendChild(taskItem);

              checkbox.checked = isChecked;
              showToast('success', message);
              reinitializateTaskTooltipsAfterDOMUpdate();
            } else {
              showToast('error', message || 'Erro ao atualizar o status de task');
              console.error("Erro:", error);
              checkbox.checked = !isChecked; 
            }
          })
          .catch((error) => {
            showToast('error', 'Something went wrong. Please try again later.');
            console.error("Erro:", error);
            checkbox.checked = !isChecked;
          });
      }
    }
  });
});


// Delete
document.addEventListener('DOMContentLoaded', function () {
  const deleteModal = document.getElementById('deleteTaskModal');
  const taskTitleInModal = document.getElementById('taskTitleInDeleteModal');
  const confirmDeleteButton = document.getElementById('confirmDeleteTaskButton');

  if (deleteModal && taskTitleInModal && confirmDeleteButton) {

      deleteModal.addEventListener('show.bs.modal', function (event) {
          const icon = event.relatedTarget; 
          if (!icon) return; 

          const taskCard = icon.closest(".task-card");
          if (!taskCard) return;

          const taskID = taskCard.getAttribute('data-id');
          const taskTitleElement = taskCard.querySelector(".task-title"); 
          const taskTitle = taskTitleElement ? taskTitleElement.textContent : 'this task'; 

          taskTitleInModal.textContent = taskTitle;
          confirmDeleteButton.setAttribute('data-task-id', taskID); 
      });

      confirmDeleteButton.addEventListener('click', function () {
        const taskID = confirmDeleteButton.getAttribute('data-task-id');
        if (!taskID) {
            console.error("Task ID não encontrado no botão de confirmação.");
            return; 
        }

        confirmDeleteButton.disabled = true;

        fetch(`/task/${projectID}/delete/${taskID}`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json"
        }})
        .then(response => response.json())
        .then(({ success, message, data, error }) => {
            const modalInstance = bootstrap.Modal.getInstance(deleteModal); 

            if (success) {
                const taskItemToRemove = document.querySelector(`.task-card[data-id="${taskID}"]`)?.closest('.task-item');
                if (taskItemToRemove) {
                    taskItemToRemove.remove();
                }
                if (modalInstance) modalInstance.hide(); 
                showToast('success', message);
            } else {
                if (modalInstance) modalInstance.hide(); o
                showToast('error', message || 'Erro ao deletar a tarefa.'); 
                console.error("Erro ao deletar tarefa:", error);
            }
        })
        .catch((error) => {
          const modalInstance = bootstrap.Modal.getInstance(deleteModal);
          if (modalInstance) modalInstance.hide(); 
          showToast('error', 'Erro de rede ao deletar a tarefa.');
          console.error(`Erro de rede: ${error}`);
        })
        .finally(() => {
            confirmDeleteButton.disabled = false; 
            confirmDeleteButton.removeAttribute('data-task-id');
        });
      });
  } else {
      if (!deleteModal) console.error("Elemento do modal de exclusão (ID: deleteTaskModal) não encontrado.");
      if (!taskTitleInModal) console.error("Elemento de título no modal de exclusão (ID: taskTitleInDeleteModal) não encontrado.");
      if (!confirmDeleteButton) console.error("Botão de confirmação de exclusão (ID: confirmDeleteTaskButton) não encontrado.");
  }
});


function formatDate(dateTimeString) {
  if (!dateTimeString) {
      return "N/A"; 
  }
  try {
      const date = new Date(dateTimeString);
      if (isNaN(date.getTime())) {
          console.error("Invalid date string received:", dateTimeString);
          return "Error"; 
      }

      // getMonth() é 0-indexado (0 = Janeiro), então some 1
      const month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
      const day = date.getUTCDate().toString().padStart(2, '0');
      const year = date.getUTCFullYear();
      const hour = date.getUTCHours().toString().padStart(2, '0');
      const minute = date.getUTCMinutes().toString().padStart(2, '0');

      return `${month}-${day}-${year} ${hour}:${minute}`;
  } catch (error) {
      console.error("Error formatting date:", isoString, error);
      return "Error";
  }
}