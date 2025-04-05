function inicializateChartContent() {
    const tasks = document.querySelectorAll('.custom-card');

    fetch('/task/get_data_for_all_doughnut_home_charts')
        .then(response => response.json())
        .then(({ success, message, data, error }) => {
            if (success) {
                console.log(message)
                const allTasksData = data.tasks;

                tasks.forEach(task => {
                    const taskId = task.getAttribute('data-id');
                    const ctx = document.getElementById(`myPieChart-${taskId}`).getContext('2d');

                    // Filtra os dados da tarefa específica
                    const taskData = allTasksData.filter(t => t.identificator === taskId);
                    if (taskData.length > 0) {
                        const labels = allTasksData.map(t => t.title);
                        const taskMinutes = allTasksData.map(t => t.minutes);
                        const totalMinutes = taskMinutes.reduce((a, b) => a + b, 0);

                        console.log('totalMinutes: ', totalMinutes)

                        if (totalMinutes < 1) {
                            console.log(`Nenhum gráfico criado, pois totalMinutes é menor que 1.`);
                            return; 
                        }

                        const percentage = ((taskMinutes[labels.indexOf(taskData[0].title)] / totalMinutes) * 100).toFixed(1);
                        const colors = allTasksData.map(t => t.identificator === taskId ? t.color : "#303030");

                        
                        console.log(`Colors:`, colors);



                        new Chart(ctx, {
                            type: 'doughnut',
                            data: {
                                labels: labels,
                                datasets: [{
                                    data: taskMinutes,
                                    backgroundColor: colors,
                                    borderColor: 'transparent',
                                    hoverBackgroundColor: colors
                                }]
                            },
                            options: {
                                cutout: '70%',
                                plugins: {
                                    legend: {
                                        display: false
                                    },
                                    tooltip: {
                                        enabled: false
                                    }
                                }
                            },
                            plugins: [{
                                id: 'centerText',
                                beforeDraw: function(chart) {
                                    const ctx = chart.ctx;
                                    const { width } = chart;
                                    const { height } = chart;
                                    const centerX = width / 2;
                                    const centerY = height / 2;

                                    const innerRadius = chart._metasets[0].data[0].innerRadius;
                                    const outerRadius = chart._metasets[0].data[0].outerRadius;

                                    // Fundo preto no centro
                                    ctx.save();
                                    ctx.beginPath();
                                    ctx.arc(centerX, centerY, innerRadius, 0, Math.PI * 2);
                                    ctx.fillStyle = '#212121';
                                    ctx.fill();
                                    ctx.restore();

                                    // Texto no centro
                                    ctx.font = 'bold 20px Arial';
                                    ctx.fillStyle = 'white';
                                    ctx.textAlign = 'center';
                                    ctx.textBaseline = 'middle';
                                    ctx.fillText(`${percentage}%`, centerX, centerY);
                                }
                            }]
                        });
                    } else {
                        document.getElementById(`myPieChart-${taskId}`).style.display = 'none';
                        console.log(`Nenhum dado disponível para a tarefa ${taskId}.`);
                    }
                });
            } else {
                showToast('error', message || 'Erro ao renderizar o gráfico de Tasks');
                console.log(error)
            }
        })
        .catch((error) => {
            showToast('error', 'Something went wrong while fetching task data.');
            console.error("Erro ao carregar os dados:", error);
        });
}

document.addEventListener('DOMContentLoaded', function() {
    inicializateChartContent();
});

function reinitializateChartContentAfterDOMUpdate(){
    inicializateChartContent();
}