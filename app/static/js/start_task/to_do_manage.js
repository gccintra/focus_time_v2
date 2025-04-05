const taskId = task_data.task_id; 

document.getElementById('createTaskToDoButton').addEventListener('click', function() {
  const ToDoName = document.getElementById('taskToDoName').value.trim();

  if (ToDoName === "") {
      showToast('error', 'Please, provide a to-do name');
      return;
  }

  fetch(`/todo/${taskId}/new_todo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: ToDoName })
  })
  .then(response => response.json())
  .then(({ success, message, data, error }) => {
      if (success) {
          const toDoHTML = `
              <div class="col-md-12 to-do-item">
                  <div class="d-flex justify-content-between align-items-center to-do-card" data-id="${data.id}">
                      <div class="to-do-text-check d-flex align-items-center">
                          <input class="form-check-input to-do-check-box me-3 mt-0 rounded-checkbox" type="checkbox" aria-label="...">
                          <span class="to-do-title mb-0">${data.title}</span>
                      </div>
                      <div class="icons">
                          <i class="bi bi-info-circle fs-4 me-3" id="infoToDo" data-bs-toggle="tooltip" data-bs-placement="left"
                              data-bs-custom-class="info-to-do-tooltip" data-bs-html="true" title="Created Time:<br>${data.created_time}">
                          </i>
                          <i class="bi bi-trash fs-4" id="deleteToDo" data-bs-toggle="modal" data-bs-target="#DeleteToDo"></i>
                      </div>
                  </div>
              </div>`;
          document.querySelector('#toDoGridInProgress').innerHTML += toDoHTML;
          $('#newTaskToDo').modal('hide');
          showToast('success', message);
          reinitializateToDoTooltipsAfterDOMUpdate();
      } else {
          showToast('error', message || 'Erro ao criar o To-Do.');
      }
  })
  .catch(() => showToast('error', 'Something went wrong. Please try again later.'));
});

// Change State REFATORAR ESSA PARTE AQUI, TA MUITO CONFUSO
document.querySelectorAll('.to-do-grid').forEach(grid => {
  grid.addEventListener('click', function (event) {
    const checkbox = event.target.closest('.to-do-check-box');
    if (checkbox) {
      const toDoCard = checkbox.closest('.to-do-card');
      const toDoItem = checkbox.closest('.to-do-item');
      if (toDoCard) {
        const toDoId = toDoCard.getAttribute('data-id');
        const isChecked = checkbox.checked;

        // Envia a requisição para o backend
        fetch(`/todo/change_state/${taskId}/${toDoId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ status: isChecked ? "completed" : "in progress",  task_id: taskId}),
        })
          .then(response => response.json())
          .then(({ success, message, data, error })  => {
            if (success) {
              const infoIcon = toDoItem.querySelector('#infoToDo');

              const currentGrid = isChecked
                ? document.querySelector('#toDoGridInProgress')
                : document.querySelector('#toDoGridCompleted');
              const newGrid = isChecked
                ? document.querySelector('#toDoGridCompleted')
                : document.querySelector('#toDoGridInProgress');

              currentGrid.removeChild(toDoItem);
            
              const toDoTitle = toDoItem.querySelector('.to-do-title');
              if (toDoTitle) {
                toDoTitle.innerHTML = isChecked
                  ? `<del>${toDoTitle.textContent}</del>`
                  : toDoTitle.textContent.replace(/<del>|<\/del>/g, "");
              }
              
              if (infoIcon) {
                if (data.status == 'completed'){
                  newTitle = `Created Time:<br>${data.created_time}
                              <br>
                              Completed Time:<br>${data.completed_time}`
                  infoIcon.setAttribute('title', newTitle);
                } else {
                  newTitle = `Created Time:<br>${data.created_time}`
                  infoIcon.setAttribute('title', newTitle);
                }
                 
              }

              newGrid.appendChild(toDoItem);

              checkbox.checked = isChecked;
              showToast('success', message);
              reinitializateToDoTooltipsAfterDOMUpdate();
            } else {
              showToast('error', message || 'Erro ao atualizar o status de To-Do');
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
  const deleteModal = document.getElementById('DeleteToDo');
  const toDoTitleInModal = document.getElementById('toDoTitleModal');
  const confirmDeleteButton = document.getElementById('confirmDeleteToDoButton');

  deleteModal.addEventListener('show.bs.modal', function (event) {
      const icon = event.relatedTarget; 
      const toDoCard = icon.closest(".to-do-card")
      const toDoId = toDoCard.getAttribute('data-id');
      const toDoTitle = toDoCard.querySelector(".to-do-title").textContent;

      
      toDoTitleInModal.textContent = toDoTitle;
      confirmDeleteButton.setAttribute('to-do-id', toDoId);

  });
  
  confirmDeleteButton.addEventListener('click', function () {
    const toDoId = confirmDeleteButton.getAttribute('to-do-id');

    fetch(`/todo/delete/${taskId}/${toDoId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json"
    }})
    .then(response => response.json())
    .then(({ success, message, data, error }) => {
        if (success) {
            document.querySelector(`.to-do-card[data-id="${toDoId}"]`).closest('.to-do-item').remove();
            $('#DeleteToDo').modal('hide'); 
            showToast('success', message);
        } else {
            $('#DeleteToDo').modal('hide'); 
            showToast('error', message)
        }
    })
    .catch((error) => {
      showToast('error', 'Something went wrong. Please try again later.');
      console.error(`Error: ${error}`);
    });
  });
});

