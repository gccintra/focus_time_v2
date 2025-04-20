const allProjectsData = data_for_script.projectsData;

function inicializateChartContent() {
    const projects = document.querySelectorAll('.custom-card');
    console.log(allProjectsData)

    projects.forEach(project => {
        const projectID = project.getAttribute('data-id');
        const canvas = document.getElementById(`myPieChart-${projectID}`);
        const ctx = canvas ? canvas.getContext('2d') : null; 

        if (!ctx) {
            console.log(`Canvas element with id myPieChart-${projectID} not found or context not available. Skipping chart initialization for this project.`);
            if (canvas) canvas.style.display = 'none'; 
            return; 
        }

        const projectData = allProjectsData.find(t => t.identificator === projectID);
       
        if (!projectData) {
            console.warn(`No data found in allProjectsData for project ID ${projectID} during initialization. Hiding canvas.`);
            if (canvas) canvas.style.display = 'none';
            return;
       }
        const currentProjectIndex = allProjectsData.findIndex(t => t.identificator === projectID);
        const currentProjectMinutes = (currentProjectIndex !== -1) ? (allProjectsData[currentProjectIndex].week_total_minutes || 0) : 0;

        if (ctx.chart) {
            console.debug(`Destroying existing chart for canvas myPieChart-${projectID}`); // Log para debug
            ctx.chart.destroy();
        }

        const labels = allProjectsData.map(t => t.title);
        const projectMinutes = allProjectsData.map(t => t.week_total_minutes);
        const totalMinutes = projectMinutes.reduce((a, b) => a + b, 0);

        if (totalMinutes < 1) {
            console.log(`Nenhum gráfico criado, pois totalMinutes é menor que 1.`);
            if (canvas) canvas.style.display = 'none'
            return; 
        }

        const percentage = totalMinutes > 0 ? ((currentProjectMinutes / totalMinutes) * 100).toFixed(1) : (currentProjectMinutes > 0 ? 100 : 0).toFixed(1);
        const colors = allProjectsData.map(t => t.identificator === projectID ? t.color : "#303030");


        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: projectMinutes,
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
        console.log(`Chart rendered for project ${projectID} with percentage ${percentage}%.`);
    });
}


document.addEventListener('DOMContentLoaded', function() {
    inicializateChartContent();
});

