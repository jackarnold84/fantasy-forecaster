"use strict";(self.webpackChunkfantasy_forecaster=self.webpackChunkfantasy_forecaster||[]).push([[84],{429:function(e,t,r){r.r(t),r.d(t,{Head:function(){return n}});var a=r(1883),l=r(7294),o=r(2437);t.default=()=>l.createElement(o.Z,null,l.createElement("div",{className:"center"},l.createElement("h2",{className:"x3-b16"},"Page Not Found"),l.createElement(a.Link,{to:"/",className:"x3-link-plain"},l.createElement("div",null,l.createElement("i",{className:"bi bi-arrow-return-left"}),l.createElement("span",{className:"x3-l8"},"Return Home")))));const n=()=>l.createElement("title",null,"Not found")},3055:function(e,t,r){r.r(t),r.d(t,{Head:function(){return L},default:function(){return W}});var a=r(7294),l=r(1728),o=r(2437),n=r(8452),i=r(3804);var c=e=>{let{children:t}=e;return a.createElement(i.Z,{top:"0"},a.createElement("h3",{className:"center"},t))};var s=e=>{let{options:t,selected:r,setSelected:l}=e;return a.createElement("div",{className:"x3-row center text"},a.createElement("span",{className:"tab-holder"},t.map((e=>a.createElement("button",{className:"tab-btn "+(e.value===r&&"tab-btn-selected"),onClick:()=>l(e.value),key:e.value},e.display)))))};var m=e=>{let{forecasts:t,week:r,teamLabels:l}=e;const[o,m]=a.useState("championship"),u=t[o][r].filter((e=>(0,n.wc)(e.prob)));return a.createElement(i.Z,{size:24},a.createElement(c,null,"Betting Odds"),a.createElement(i.Z,{top:"0"},a.createElement(s,{options:[{display:"Playoffs",value:"playoffs"},{display:"Championship",value:"championship"},{display:"Punishment",value:"punishment"}],selected:o,setSelected:m})),a.createElement(i.Z,null,a.createElement("table",{className:"x3-table",style:{maxWidth:"200px"}},a.createElement("tbody",null,u.map((e=>a.createElement("tr",{key:e.team},a.createElement("td",null,l[e.team]),a.createElement("td",{style:{textAlign:"center"}},(0,n.wc)(e.prob))))))),0===u.length&&a.createElement(i.Z,{size:32},a.createElement("div",{className:"center"},a.createElement("i",null,"No bets available")))))},u=r(5785),d=r(7566),p=r(8356),h=r.n(p);const b={style:{width:"100%",height:"100%"},useResizeHandler:!0},g={displayModeBar:!1,showTips:!1,responsive:!0},f={template:{data:{barpolar:[{marker:{line:{color:"white",width:.5},pattern:{fillmode:"overlay",size:10,solidity:.2}},type:"barpolar"}],bar:[{error_x:{color:"rgb(36,36,36)"},error_y:{color:"rgb(36,36,36)"},marker:{line:{color:"white",width:.5},pattern:{fillmode:"overlay",size:10,solidity:.2}},type:"bar"}],carpet:[{aaxis:{endlinecolor:"rgb(36,36,36)",gridcolor:"white",linecolor:"white",minorgridcolor:"white",startlinecolor:"rgb(36,36,36)"},baxis:{endlinecolor:"rgb(36,36,36)",gridcolor:"white",linecolor:"white",minorgridcolor:"white",startlinecolor:"rgb(36,36,36)"},type:"carpet"}],choropleth:[{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"},type:"choropleth"}],contourcarpet:[{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"},type:"contourcarpet"}],contour:[{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"},colorscale:[[0,"#440154"],[.1111111111111111,"#482878"],[.2222222222222222,"#3e4989"],[.3333333333333333,"#31688e"],[.4444444444444444,"#26828e"],[.5555555555555556,"#1f9e89"],[.6666666666666666,"#35b779"],[.7777777777777778,"#6ece58"],[.8888888888888888,"#b5de2b"],[1,"#fde725"]],type:"contour"}],heatmapgl:[{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"},colorscale:[[0,"#440154"],[.1111111111111111,"#482878"],[.2222222222222222,"#3e4989"],[.3333333333333333,"#31688e"],[.4444444444444444,"#26828e"],[.5555555555555556,"#1f9e89"],[.6666666666666666,"#35b779"],[.7777777777777778,"#6ece58"],[.8888888888888888,"#b5de2b"],[1,"#fde725"]],type:"heatmapgl"}],heatmap:[{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"},colorscale:[[0,"#440154"],[.1111111111111111,"#482878"],[.2222222222222222,"#3e4989"],[.3333333333333333,"#31688e"],[.4444444444444444,"#26828e"],[.5555555555555556,"#1f9e89"],[.6666666666666666,"#35b779"],[.7777777777777778,"#6ece58"],[.8888888888888888,"#b5de2b"],[1,"#fde725"]],type:"heatmap"}],histogram2dcontour:[{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"},colorscale:[[0,"#440154"],[.1111111111111111,"#482878"],[.2222222222222222,"#3e4989"],[.3333333333333333,"#31688e"],[.4444444444444444,"#26828e"],[.5555555555555556,"#1f9e89"],[.6666666666666666,"#35b779"],[.7777777777777778,"#6ece58"],[.8888888888888888,"#b5de2b"],[1,"#fde725"]],type:"histogram2dcontour"}],histogram2d:[{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"},colorscale:[[0,"#440154"],[.1111111111111111,"#482878"],[.2222222222222222,"#3e4989"],[.3333333333333333,"#31688e"],[.4444444444444444,"#26828e"],[.5555555555555556,"#1f9e89"],[.6666666666666666,"#35b779"],[.7777777777777778,"#6ece58"],[.8888888888888888,"#b5de2b"],[1,"#fde725"]],type:"histogram2d"}],histogram:[{marker:{line:{color:"white",width:.6}},type:"histogram"}],mesh3d:[{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"},type:"mesh3d"}],parcoords:[{line:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},type:"parcoords"}],pie:[{automargin:!0,type:"pie"}],scatter3d:[{line:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},marker:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},type:"scatter3d"}],scattercarpet:[{marker:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},type:"scattercarpet"}],scattergeo:[{marker:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},type:"scattergeo"}],scattergl:[{marker:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},type:"scattergl"}],scattermapbox:[{marker:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},type:"scattermapbox"}],scatterpolargl:[{marker:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},type:"scatterpolargl"}],scatterpolar:[{marker:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},type:"scatterpolar"}],scatter:[{marker:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},type:"scatter"}],scatterternary:[{marker:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},type:"scatterternary"}],surface:[{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"},colorscale:[[0,"#440154"],[.1111111111111111,"#482878"],[.2222222222222222,"#3e4989"],[.3333333333333333,"#31688e"],[.4444444444444444,"#26828e"],[.5555555555555556,"#1f9e89"],[.6666666666666666,"#35b779"],[.7777777777777778,"#6ece58"],[.8888888888888888,"#b5de2b"],[1,"#fde725"]],type:"surface"}],table:[{cells:{fill:{color:"rgb(237,237,237)"},line:{color:"white"}},header:{fill:{color:"rgb(217,217,217)"},line:{color:"white"}},type:"table"}]},layout:{annotationdefaults:{arrowhead:0,arrowwidth:1},autotypenumbers:"strict",coloraxis:{colorbar:{outlinewidth:1,tickcolor:"rgb(36,36,36)",ticks:"outside"}},colorscale:{diverging:[[0,"rgb(103,0,31)"],[.1,"rgb(178,24,43)"],[.2,"rgb(214,96,77)"],[.3,"rgb(244,165,130)"],[.4,"rgb(253,219,199)"],[.5,"rgb(247,247,247)"],[.6,"rgb(209,229,240)"],[.7,"rgb(146,197,222)"],[.8,"rgb(67,147,195)"],[.9,"rgb(33,102,172)"],[1,"rgb(5,48,97)"]],sequential:[[0,"#440154"],[.1111111111111111,"#482878"],[.2222222222222222,"#3e4989"],[.3333333333333333,"#31688e"],[.4444444444444444,"#26828e"],[.5555555555555556,"#1f9e89"],[.6666666666666666,"#35b779"],[.7777777777777778,"#6ece58"],[.8888888888888888,"#b5de2b"],[1,"#fde725"]],sequentialminus:[[0,"#440154"],[.1111111111111111,"#482878"],[.2222222222222222,"#3e4989"],[.3333333333333333,"#31688e"],[.4444444444444444,"#26828e"],[.5555555555555556,"#1f9e89"],[.6666666666666666,"#35b779"],[.7777777777777778,"#6ece58"],[.8888888888888888,"#b5de2b"],[1,"#fde725"]]},colorway:["#1F77B4","#FF7F0E","#2CA02C","#D62728","#9467BD","#8C564B","#E377C2","#7F7F7F","#BCBD22","#17BECF"],font:{family:"Source Sans Pro",color:"rgb(36,36,36)",size:"16"},geo:{bgcolor:"white",lakecolor:"white",landcolor:"white",showlakes:!0,showland:!0,subunitcolor:"white"},hoverlabel:{align:"left"},hovermode:"closest",mapbox:{style:"light"},paper_bgcolor:"white",plot_bgcolor:"white",polar:{angularaxis:{gridcolor:"rgb(232,232,232)",linecolor:"rgb(36,36,36)",showgrid:!1,showline:!0,ticks:"outside"},bgcolor:"white",radialaxis:{gridcolor:"rgb(232,232,232)",linecolor:"rgb(36,36,36)",showgrid:!1,showline:!0,ticks:"outside"}},scene:{xaxis:{backgroundcolor:"white",gridcolor:"rgb(232,232,232)",gridwidth:2,linecolor:"rgb(36,36,36)",showbackground:!0,showgrid:!1,showline:!0,ticks:"outside",zeroline:!1,zerolinecolor:"rgb(36,36,36)"},yaxis:{backgroundcolor:"white",gridcolor:"rgb(232,232,232)",gridwidth:2,linecolor:"rgb(36,36,36)",showbackground:!0,showgrid:!1,showline:!0,ticks:"outside",zeroline:!1,zerolinecolor:"rgb(36,36,36)"},zaxis:{backgroundcolor:"white",gridcolor:"rgb(232,232,232)",gridwidth:2,linecolor:"rgb(36,36,36)",showbackground:!0,showgrid:!1,showline:!0,ticks:"outside",zeroline:!1,zerolinecolor:"rgb(36,36,36)"}},shapedefaults:{fillcolor:"black",line:{width:0},opacity:.3},ternary:{aaxis:{gridcolor:"rgb(232,232,232)",linecolor:"rgb(36,36,36)",showgrid:!1,showline:!0,ticks:"outside"},baxis:{gridcolor:"rgb(232,232,232)",linecolor:"rgb(36,36,36)",showgrid:!1,showline:!0,ticks:"outside"},bgcolor:"white",caxis:{gridcolor:"rgb(232,232,232)",linecolor:"rgb(36,36,36)",showgrid:!1,showline:!0,ticks:"outside"}},title:{x:.05},xaxis:{automargin:!0,gridcolor:"rgb(232,232,232)",linecolor:"rgb(36,36,36)",showgrid:!1,showline:!0,ticks:"outside",title:{standoff:15},zeroline:!1,zerolinecolor:"rgb(36,36,36)"},yaxis:{automargin:!0,gridcolor:"rgb(232,232,232)",linecolor:"rgb(36,36,36)",showgrid:!1,showline:!0,ticks:"outside",title:{standoff:15},zeroline:!1,zerolinecolor:"rgb(36,36,36)"}}},dragmode:!1,margin:{t:10,b:10,l:10,r:10}};var y=e=>{let{data:t,height:l,xaxis:o={},yaxis:n={}}=e;const i=h()({loader:()=>Promise.all([r.e(960),r.e(660)]).then(r.bind(r,8660)),loading(){return a.createElement("div",{style:{height:l,display:"flex",justifyContent:"center",alignItems:"center"}},a.createElement("div",{className:"loader"}))}});return a.createElement("div",{style:{minHeight:l}},a.createElement(i,Object.assign({data:[{type:"bar",orientation:"h",texttemplate:"%{x}",textposition:"outside",name:"",hovertemplate:"%{y}<br> %{x}",...t}],layout:{height:l,xaxis:{visible:!1,fixedrange:!0,...o},yaxis:{fixedrange:!0,...n},...f},config:g},b)))};var E=e=>{let{min:t,max:r,week:l,setWeek:o}=e;return a.createElement("div",{className:"center"},a.createElement("button",{className:"nav-button",disabled:l<=t,onClick:()=>{o(l-1)}},a.createElement("i",{className:"bi bi-caret-left-fill"})),a.createElement("span",{style:{display:"inline-block",minWidth:"72px"}},0===l?"Preseason":"Week "+l),a.createElement("button",{className:"nav-button",disabled:l>=r,onClick:()=>{o(l+1)}},a.createElement("i",{className:"bi bi-caret-right-fill"})))};const w={playoffs:d.DG.orange,championship:d.DG.green,punishment:d.DG.red},k={playoffs:"Make Playoffs",championship:"Win Championship",punishment:"League Punishment"};var x=e=>{let{forecasts:t,week:r}=e;const[l,o]=a.useState(r),[n,m]=a.useState("playoffs"),d=t[n][l].map((e=>100*e.prob)).reverse(),p=t[n][l].map((e=>e.team)).reverse(),h=Math.max.apply(Math,(0,u.Z)(d));return a.createElement(i.Z,{size:24},a.createElement(c,null,"Forecasts"),a.createElement(i.Z,null,a.createElement(E,{min:0,max:r,week:l,setWeek:o})),a.createElement(i.Z,{top:"0"},a.createElement(s,{options:[{display:"Playoffs",value:"playoffs"},{display:"Championship",value:"championship"},{display:"Punishment",value:"punishment"}],selected:n,setSelected:m})),a.createElement(i.Z,{width:500},a.createElement("div",{className:"center"},k[n]),a.createElement(y,{data:{x:d,y:p,marker:{color:w[n]},hovertemplate:"%{y}<br> %{x:.1f}%"},height:350,xaxis:{ticksuffix:"%",range:[0,1.2*h]}})))};var v=e=>{let{children:t}=e;return a.createElement(i.Z,{top:16},a.createElement("div",{className:"auto center subtext",style:{maxWidth:"400px"}},t))};const N=e=>{let{value:t}=e;const r=t>=1?d.DG.green:t<=-1?d.DG.red:"black";return a.createElement("td",{style:{color:r}},t>=0?"+"+t:t)};var Z=e=>{let{expectedWins:t,sos:r,teamLabels:l}=e;const[o,n]=a.useState("wins");return a.createElement(i.Z,{size:24},a.createElement(c,null,"Strength of Schedule"),a.createElement(i.Z,{top:"0"},a.createElement(s,{options:[{display:"Expected Wins",value:"wins"},{display:"Points Against",value:"points"}],selected:o,setSelected:n})),"wins"===o&&a.createElement(i.Z,null,a.createElement("table",{className:"x3-table x3-bordered"},a.createElement("tbody",null,a.createElement("tr",{className:"th-border"},a.createElement("th",null,"Team"),a.createElement("th",null,"Expected"),a.createElement("th",null,"Actual"),a.createElement("th",null,"Difference")),t.map((e=>a.createElement("tr",{key:e.team},a.createElement("td",null,l[e.team]),a.createElement("td",null,e.expected.toFixed(1)),a.createElement("td",null,e.actual),a.createElement(N,{value:e.diff.toFixed(1)})))))),a.createElement(v,null,"Shows expected number of wins if the schedule was re-randomized")),"points"===o&&a.createElement(i.Z,null,a.createElement("table",{className:"x3-table x3-bordered"},a.createElement("tbody",null,a.createElement("tr",{className:"th-border"},a.createElement("th",null,"Team"),a.createElement("th",null,"Current"),a.createElement("th",null,"Future")),r.map((e=>a.createElement("tr",{key:e.team},a.createElement("td",null,l[e.team]),a.createElement("td",null,e.current.toFixed(1)),a.createElement("td",null,e.future>0?e.future.toFixed(1):"--")))))),a.createElement(v,null,"Shows average points against and expected points against for the remainder of the season")))};var S=e=>{let{standings:t,teamLabels:r}=e;return a.createElement(i.Z,{size:16},a.createElement(c,null,"Standings"),a.createElement(i.Z,null,a.createElement("table",{className:"x3-table x3-bordered"},a.createElement("tbody",null,a.createElement("tr",{className:"th-border"},a.createElement("th",{"aria-label":"rank"}),a.createElement("th",{"aria-label":"space"}),a.createElement("th",null,"Team"),a.createElement("th",null,"Wins"),a.createElement("th",null,"Avg")),t.league.map((e=>a.createElement("tr",{key:e.rank},a.createElement("td",null,e.rank),a.createElement("td",null),a.createElement("td",null,r[e.team]),a.createElement("td",null,e.wins),a.createElement("td",null,e.avg.toFixed(1)))))))))};var C=e=>{let{ratings:t,week:r}=e;const[l,o]=a.useState(r),[m,p]=a.useState("OVR"),h=Object.keys(t[0]).map((e=>({display:e,value:e}))),b=t[l][m].map((e=>e.rating)).reverse(),g=t[l][m].map((e=>e.team)).reverse(),f=Math.max.apply(Math,(0,u.Z)(b)),w=Math.min.apply(Math,(0,u.Z)(b)),k=Math.max(Math.min(w-10,50),0);return a.createElement(i.Z,{size:24},a.createElement(c,null,"Team Ratings"),a.createElement(i.Z,null,a.createElement(E,{min:0,max:r,week:l,setWeek:o})),a.createElement(i.Z,{top:"0"},a.createElement(s,{options:h,selected:m,setSelected:p})),a.createElement(i.Z,{width:500},a.createElement("div",{className:"center"},(0,n.YR)(m)),a.createElement(y,{data:{x:b,y:g,marker:{color:d.Uj[m]},texttemplate:"%{x:.0f}",hovertemplate:"%{y}<br> %{x:.1f}"},height:300,xaxis:{range:[k,1.1*f]}})))};r(3792);var z=e=>{let{data:t,height:l,xaxis:o={},yaxis:n={}}=e;const i=h()({loader:()=>Promise.all([r.e(960),r.e(660)]).then(r.bind(r,8660)),loading(){return a.createElement("div",{style:{height:l,display:"flex",justifyContent:"center",alignItems:"center"}},a.createElement("div",{className:"loader"}))}});return a.createElement("div",{style:{minHeight:l}},a.createElement(i,Object.assign({data:t.map((e=>({type:"scatter",hovertemplate:"Week %{x}<br> %{y}",...e}))),layout:{height:l,xaxis:{fixedrange:!0,...o,tickfont:{size:14}},yaxis:{fixedrange:!0,...n,tickfont:{size:14}},legend:{orientation:"h",y:-.2},...f},config:g},b)))};const T={playoffs:"Make Playoffs",championship:"Win Championship",punishment:"League Punishment"};var _=e=>{let{forecasts:t,teamLabels:r}=e;const[l,o]=a.useState("playoffs"),[n,m]=a.useState("all"),p=Object.keys(r).sort(),h=t[l].flat(),b=p.map(((e,t)=>{const r=h.filter((t=>t.team===e));return{name:e,x:r.map((e=>e.week)),y:r.map((e=>100*e.prob)),marker:{color:d.Xz[t]},visible:"all"===n||n===e||"legendonly"}})),g=Math.max.apply(Math,(0,u.Z)(h.map((e=>100*e.prob))));return a.createElement(i.Z,{size:24},a.createElement(c,null,"Forecasts Over Time"),a.createElement(i.Z,{top:"0"},a.createElement(s,{options:[{display:"Playoffs",value:"playoffs"},{display:"Championship",value:"championship"},{display:"Punishment",value:"punishment"}],selected:l,setSelected:o})),a.createElement(i.Z,{width:150},a.createElement("select",{className:"x3-select",onChange:e=>m(e.target.value)},a.createElement("option",{value:"all"},"All Teams"),p.map((e=>a.createElement("option",{key:e,value:e},e))))),a.createElement(i.Z,{width:500},a.createElement("div",{className:"center"},T[l]),a.createElement(z,{data:b,height:350,yaxis:{ticksuffix:"%",range:[-4,g+4]}})))};const P=e=>{let{value:t}=e;const r=(t/90).toFixed(2);return a.createElement("td",{style:{backgroundColor:"rgb(81, 157, 233, "+r+")"}},t)};var O=e=>{let{matchupImportance:t,teamLabels:r,week:l}=e;const[o,n]=a.useState(l),s=o>0&&!t[o];return a.createElement(i.Z,{size:24},a.createElement(c,null,"Upcoming Games"),a.createElement(i.Z,null,a.createElement(E,{min:1,max:l,week:o,setWeek:n})),a.createElement(i.Z,null,s?a.createElement(i.Z,{size:32},a.createElement("div",{className:"center"},a.createElement("i",null,"Playoffs In Progress"))):a.createElement("table",{className:"x3-table x3-bordered",style:{maxWidth:"400px",tableLayout:"fixed"}},a.createElement("tbody",null,a.createElement("tr",{className:"th-border"},a.createElement("th",{"aria-label":"away"},"Matchup"),a.createElement("th",{"aria-label":"vs",width:"40px"}),a.createElement("th",{"aria-label":"home"}),a.createElement("th",{width:"80px"},"Importance")),t[o].map((e=>a.createElement("tr",{key:e.home},a.createElement("td",null,r[e.away]),a.createElement("td",null,"vs"),a.createElement("td",null,r[e.home]),a.createElement(P,{value:e.importance}))))))))};var F=e=>{let{meta:t}=e;return a.createElement("span",null,a.createElement("img",{src:t.img,height:18,alt:t.team,style:{verticalAlign:"top",paddingRight:"10px"}}),t.name)};var M=e=>{let{sportTag:t,leagueTag:r}=e;const o=l[t][r],c=o.meta.name,s=(0,n.kC)(o.meta.sport),u=o.meta.year,d=parseInt(o.meta.week),p=Object.fromEntries(Object.values(o.teams.metadata).map((e=>[e.name,a.createElement(F,{meta:e})])));return a.createElement(i.Z,{top:2},a.createElement("div",{className:"center"},a.createElement(i.Z,{top:2},a.createElement("h4",{className:"medium-weight x3-b4"},u),a.createElement("h2",null,c," Fantasy ",s)),a.createElement(i.Z,{size:24},a.createElement("h4",null,"Week ",d," Report"))),a.createElement(S,{standings:o.league.standings,teamLabels:p}),a.createElement(O,{matchupImportance:o.league.matchupImportance,teamLabels:p,week:d}),a.createElement(x,{forecasts:o.league.forecasts,week:d}),a.createElement(C,{ratings:o.teams.ratings,week:d}),a.createElement(m,{forecasts:o.league.forecasts,week:d,teamLabels:p}),a.createElement(Z,{expectedWins:o.league.expectedWins,sos:o.league.sos,teamLabels:p}),a.createElement(_,{forecasts:o.league.forecasts,teamLabels:p}))};r(429);var W=e=>{const t=e.params.sport,r=e.params.league,n=t in l&&r in l[t];return console.log((new Date).getTime(),t,r),n?a.createElement(o.Z,null,a.createElement(M,{sportTag:t,leagueTag:r})):a.createElement("h1",null,"NOT VALID")};const L=()=>a.createElement("title",null,"Fantasy Forecaster")},8356:function(e,t,r){var a="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e};function l(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function o(e,t){if(!e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!t||"object"!=typeof t&&"function"!=typeof t?e:t}function n(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function, not "+typeof t);e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,enumerable:!1,writable:!0,configurable:!0}}),t&&(Object.setPrototypeOf?Object.setPrototypeOf(e,t):e.__proto__=t)}var i=r(7294),c=r(5697),s=[],m=[];function u(e){var t=e(),r={loading:!0,loaded:null,error:null};return r.promise=t.then((function(e){return r.loading=!1,r.loaded=e,e})).catch((function(e){throw r.loading=!1,r.error=e,e})),r}function d(e){var t={loading:!1,loaded:{},error:null},r=[];try{Object.keys(e).forEach((function(a){var l=u(e[a]);l.loading?t.loading=!0:(t.loaded[a]=l.loaded,t.error=l.error),r.push(l.promise),l.promise.then((function(e){t.loaded[a]=e})).catch((function(e){t.error=e}))}))}catch(a){t.error=a}return t.promise=Promise.all(r).then((function(e){return t.loading=!1,e})).catch((function(e){throw t.loading=!1,e})),t}function p(e,t){return i.createElement((r=e)&&r.__esModule?r.default:r,t);var r}function h(e,t){var u,d;if(!t.loading)throw new Error("react-loadable requires a `loading` component");var h=Object.assign({loader:null,loading:null,delay:200,timeout:null,render:p,webpack:null,modules:null},t),b=null;function g(){return b||(b=e(h.loader)),b.promise}return s.push(g),"function"==typeof h.webpack&&m.push((function(){if(e=h.webpack,"object"===a(r.m)&&e().every((function(e){return void 0!==e&&void 0!==r.m[e]})))return g();var e})),d=u=function(t){function r(a){l(this,r);var n=o(this,t.call(this,a));return n.retry=function(){n.setState({error:null,loading:!0,timedOut:!1}),b=e(h.loader),n._loadModule()},g(),n.state={error:b.error,pastDelay:!1,timedOut:!1,loading:b.loading,loaded:b.loaded},n}return n(r,t),r.preload=function(){return g()},r.prototype.componentWillMount=function(){this._mounted=!0,this._loadModule()},r.prototype._loadModule=function(){var e=this;if(this.context.loadable&&Array.isArray(h.modules)&&h.modules.forEach((function(t){e.context.loadable.report(t)})),b.loading){"number"==typeof h.delay&&(0===h.delay?this.setState({pastDelay:!0}):this._delay=setTimeout((function(){e.setState({pastDelay:!0})}),h.delay)),"number"==typeof h.timeout&&(this._timeout=setTimeout((function(){e.setState({timedOut:!0})}),h.timeout));var t=function(){e._mounted&&(e.setState({error:b.error,loaded:b.loaded,loading:b.loading}),e._clearTimeouts())};b.promise.then((function(){t()})).catch((function(e){t()}))}},r.prototype.componentWillUnmount=function(){this._mounted=!1,this._clearTimeouts()},r.prototype._clearTimeouts=function(){clearTimeout(this._delay),clearTimeout(this._timeout)},r.prototype.render=function(){return this.state.loading||this.state.error?i.createElement(h.loading,{isLoading:this.state.loading,pastDelay:this.state.pastDelay,timedOut:this.state.timedOut,error:this.state.error,retry:this.retry}):this.state.loaded?h.render(this.state.loaded,this.props):null},r}(i.Component),u.contextTypes={loadable:c.shape({report:c.func.isRequired})},d}function b(e){return h(u,e)}b.Map=function(e){if("function"!=typeof e.render)throw new Error("LoadableMap requires a `render(loaded, props)` function");return h(d,e)};var g=function(e){function t(){return l(this,t),o(this,e.apply(this,arguments))}return n(t,e),t.prototype.getChildContext=function(){return{loadable:{report:this.props.report}}},t.prototype.render=function(){return i.Children.only(this.props.children)},t}(i.Component);function f(e){for(var t=[];e.length;){var r=e.pop();t.push(r())}return Promise.all(t).then((function(){if(e.length)return f(e)}))}g.propTypes={report:c.func.isRequired},g.childContextTypes={loadable:c.shape({report:c.func.isRequired}).isRequired},b.Capture=g,b.preloadAll=function(){return new Promise((function(e,t){f(s).then(e,t)}))},b.preloadReady=function(){return new Promise((function(e,t){f(m).then(e,e)}))},e.exports=b}}]);
//# sourceMappingURL=component---src-pages-[league]-[sport]-league-js-415e919e39b87d19f6d7.js.map