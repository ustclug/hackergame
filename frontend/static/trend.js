"use strict";

const n = 10;
window.onload = function () {
  axios.post('/admin/challenge/', {method: 'get_all'})
    .then(({data: {value}}) => {
      const challenges = value;
      var reqs = [];
      for (var i = 0; i < n; i++) {
        reqs.push(
          axios.post('/admin/submission/', {
            method: 'get_user_progress',
            args: {user: app.objs[i].user},
          })
        );
      }
      axios.all(reqs)
        .then(responses => {
          var data = [];

          var mintime = null;
          var maxtime = null;
          for (var i = 0; i < n; i++) {
            const flags = responses[i].data.value.flags;
            for (var j = 0; j < flags.length; j++) {
              const t = new Date(flags[j].time);
              if (mintime == null || t < mintime) {
                mintime = t;
              }
              if (maxtime == null || t > maxtime) {
                maxtime = t;
              }
            }
          }

          for (var i = 0; i < n; i++) {
            var points = [];
            const flags = responses[i].data.value.flags;
            var score = 0;
            points.push({
              x: mintime,
              y: 0,
            });
            for (var j = 0; j < flags.length; j++) {
              points.push({
                x: new Date(flags[j].time),
                y: score,
              });
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
              x: maxtime,
              y: score,
            });
            data.push({
              type: "line",
              name: app.users[app.objs[i].user],
              showInLegend: true,
              dataPoints: points,
              markerSize: 0,
            });
          }
          console.log(data);
          new CanvasJS.Chart('chart', {
            legend: {
              verticalAlign: "top",
              horizontalAlign: "center",
            },
            toolTip: {
              shared: true,
            },
            data: data,
          }).render();
        });
    });
};
