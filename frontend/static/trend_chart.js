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
    let starttime = triggers.find(i => i.state);
    if (!starttime || new Date(starttime.time) > new Date()) {
      document.getElementById('chart').innerHTML = '比赛尚未开始';
      return;
    } else {
      starttime = new Date(starttime.time);
    }
    let endtime = [...triggers].reverse().find(i => !i.state);
    endtime = endtime ? new Date(endtime.time) : new Date();
    if (endtime > new Date()) {
      endtime = new Date();
    }
    let data = user_reqs.map(({data: {value: history}}, i) => {
      let points = history.map(i => ({x: new Date(i.time), y: i.score}));
      points.unshift({x: starttime, y: 0});
      points.push({x: endtime, y: points[points.length-1].y});
      let username = app.users[app.objs[i].user];
      let color = ["#C0392B", "#2ECC71", "#3498DB", "#F1C40F", "#8E44AD", "#797D7F", "#117864", "#E67E22", "#F1948A", "#1F618D"][i];
      return {
        label: username,
        data: points,
        steppedLine: true,
        fill: false,
        backgroundColor: color,
        borderColor: color,
        borderWidth: 2,
      };
    });

    new Chart(document.getElementById('chart').getContext('2d'),{
      type: 'line',
      data: {
        datasets: data,
      },
      options: {
        responsive: false,
        scales: {
					xAxes: [{
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
            }
					}]
				}
      }
    });
  });
}
