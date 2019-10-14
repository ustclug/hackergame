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
