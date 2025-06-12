document.addEventListener("DOMContentLoaded", function () {
    // Graphique des ventes
    var ctx1 = document.getElementById("salesChart").getContext("2d");
    var salesChart = new Chart(ctx1, {
        type: "line",
        data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            datasets: [{
                label: "Sales",
                data: [10, 20, 30, 40, 50, 60],
                borderColor: "blue",
                fill: false
            }]
        }
    });

    // Graphique des commandes
    var ctx2 = document.getElementById("ordersChart").getContext("2d");
    var ordersChart = new Chart(ctx2, {
        type: "bar",
        data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            datasets: [{
                label: "Orders",
                data: [50, 40, 30, 20, 10, 5],
                backgroundColor: "red"
            }]
        }
    });
});
