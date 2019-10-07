"use strict";

function drawchart() {
  axios.all([
    axios.all(app.objs.slice(0, 10).map(i => (
      axios.post('/admin/submission/', {
        method: 'get_user_progress',
        args: {user: i.user},
      })
    ))),
    axios.post('/admin/challenge/', {method: 'get_all'}),
    axios.post('/admin/trigger/', {method: 'get_all'}),
  ]).then(([users, challenges, triggers]) => {
    triggers = triggers.data.value;
    triggers.sort((a, b) => new Date(a.time) - new Date(b.time));
    challenges = challenges.data.value;
    let starttime = triggers.find(i => i.state);
    let endtime = [...triggers].reverse().find(i => !i.state);
    if (!endtime || endtime > new Date()) {
      endtime = new Date();
    }
    let data = users.map((req, i) => {
      let points = [];
      let score = 0;
      points.push({x: starttime, y: score});
      for (let flag of req.data.value.flags) {
        let challenge = challenges.find(i => i.pk === flag.challenge);
        score += challenge.flags[flag.flag].score;
        points.push({x: new Date(flag.time), y: score});
      }
      points.push({x: endtime, y: score});
      return {
        type: 'stepLine',
        name: app.users[app.objs[i].user],
        showInLegend: true,
        dataPoints: points,
        markerSize: 0,
      };
    });
    new CanvasJS.Chart('chart', {
      legend: {
        verticalAlign: "top",
        horizontalAlign: "center",
      },
      toolTip: {
        content: "{name}: {y}",
      },
      data: data,
      animationEnabled: true,
      zoomEnabled: true,
      exportEnabled: true,
      axisX: {
        valueFormatString: "MM-DD HH:mm",
        labelAngle: -50,
        crosshair: {
          enabled: true,
        },
      },
    }).render();
  });
}
