"use strict";

var drawchart = function () {
  var reqs = [];
  const n = app.objs.length < 10 ? app.objs.length : 10;
  for (var i = 0; i < n; i++) {
    reqs.push(
      axios.post('/admin/submission/', {
        method: 'get_user_progress',
        args: {user: app.objs[i].user},
      })
    );
  }
  reqs.push(axios.post('/admin/challenge/', {method: 'get_all'}))
  reqs.push(axios.post('/admin/trigger/', {method: 'get_all'}))
  axios.all(reqs)
    .then(responses => {
      const challenges = responses[n].data.value
      const triggers = responses[n + 1].data.value
      var data = [];
      var starttime = null;
      var endtime = null;
      for (var i = 0; i < triggers.length; i++) {
        const t = new Date(triggers[i].time);
        if (triggers[i].state) {
          if (starttime == null || t < starttime) {
            starttime = t;
          }
        } else {
          if (endtime == null || t > endtime) {
            endtime = t;
          }
        }
        if (endtime == null || endtime > new Date()) {
          endtime = new Date();
        }
      }

      for (var i = 0; i < n; i++) {
        var points = [];
        const flags = responses[i].data.value.flags;
        var score = 0;
        points.push({
          x: starttime,
          y: 0,
        });
        for (var j = 0; j < flags.length; j++) {
          for(var k = 0; k < challenges.length; k++) {
            if (challenges[k].pk == flags[j].challenge) {
              score += challenges[k].flags[flags[j].flag].score;
              break;
            }
          }
          points.push({
            x: new Date(flags[j].time),
            y: score,
          });
        }
        points.push({
          x: endtime,
          y: score,
        });
        data.push({
          type: "stepLine",
          name: app.users[app.objs[i].user],
          showInLegend: true,
          dataPoints: points,
          markerSize: 0,
        });
      }
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
        axisX:{
          valueFormatString: "MM-DD HH:mm" ,
          labelAngle: -50,
          crosshair: {
            enabled: true
          }
      },
      }).render();
    });
};
