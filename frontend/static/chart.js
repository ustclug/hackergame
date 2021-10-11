"use strict";

function drawchart() {
  axios.all([
    axios.all(app.objs.slice(0, 10).map(i => (
      axios.post('/admin/submission/', {
        method: 'get_user_history',
        args: {user: i.user},
      })
    ))),
    axios.post('/admin/trigger/', {method: 'get_all'}),
  ]).then(([user_reqs, {data: {value: triggers}}]) => {
    let starttime = triggers.find(i => i.can_submit);
    if (!starttime || new Date(starttime.time) > new Date()) {
      document.getElementById('charttext').innerHTML = '比赛尚未开始';
      return;
    } else {
      starttime = new Date(starttime.time);
    }
    let last_starttime = [...triggers].reverse().find(i => i.can_submit);
    let endtime = [...triggers].reverse().find(i => !i.can_submit);
    if (!endtime || new Date(endtime.time) > new Date() || new Date(endtime.time) < new Date(last_starttime.time)) {
      endtime = new Date();
    } else {
      endtime = new Date(endtime.time);
    }
    let data = user_reqs.map(({data: {value: history}}, i) => {
      let points = history.map(i => ({x: new Date(i.time), y: i.score}));
      points.unshift({x: starttime, y: 0});
      points.push({x: endtime, y: points[points.length-1].y});
      let username = app.users[app.objs[i].user].display_name;
      let color = ["#C0392B", "#2ECC71", "#3498DB", "#F1C40F", "#8E44AD", "#797D7F", "#117864", "#E67E22", "#F1948A", "#1F618D"][i];
      return {
        label: username,
        data: points,
        stepped: true,
        fill: false,
        backgroundColor: color,
        borderColor: color,
        borderWidth: 2,
        radius: 2,
        hoverRadius: 3,
      };
    });

    document.getElementById('charttext').innerHTML = '';

    new Chart(document.getElementById('chart').getContext('2d'),{
      type: 'line',
      data: {
        datasets: data,
      },
      options: {
        hover: {
          mode: 'x',
        },
        responsive: false,
        scales: {
          x: {
            type: 'time',
            ticks: {
              minRotation: 50,
            },
            time: {
              unit: 'hour',
              displayFormats: {
                hour: "MM-DD HH:mm",
              },
              tooltipFormat: "YYYY-MM-DD HH:mm:ss",
            },
          },
        },
      },
    });
  });
}
