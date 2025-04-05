document.addEventListener("DOMContentLoaded", function () {
    fetch('/task/get_data_for_last_365_days_home_chart')
    .then(response => response.json())
    .then(({ success, message, data, error }) => {
        if (success) {
            const minutes_per_day = data.minutes_per_day;
        
            $('#heatmap-container').heatmap({
                data: minutes_per_day,
                cellSize: 25,
                gutter: 6,
                colors: {
                    0: '#303030',
                    0.25: '#1b3b2b',
                    0.5: '#085e30',
                    0.75: '#0f943b',
                    1: '#1fc443 '
                },
                locale: 'en-US',
                debug: true // To check if data loads correctly in console
            });

            // Initialize tooltips for heatmap cells after rendering
            $('#heatmap-container').on('post.heatmap', function () {
                $('.heatmap-cell[data-bs-toggle="tooltip"]').tooltip({
                    customClass: 'info-tooltip'
                });
            });
        } else {
            showToast('error', message || 'Erro ao renderizar o gráfico de 365 days');
            console.log(error)
        }
    })
    .catch((error) => {
        showToast('error', 'Something went wrong while fetching task data.');
        console.error("Erro ao carregar os dados:", error);
    }); 
});
