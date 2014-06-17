$(function () {

    $.ajaxSetup({ cache: false });

    console.log(".---------------------------.");
    console.log("| *   Starting Robotina   * |");
    console.log("'---------------------------'");

    var canvas = document.getElementById('myCanvas');
    var context = canvas.getContext('2d');
    var graph = null;

    var pusher = new Pusher('60ac382824573be1ddd2');
    var channel = pusher.subscribe('robotina');

    channel.bind('map', function(data) {
        graph =  $.parseJSON(data.map) ;
        console.log(graph);
        drawGraph(graph);
    });
    
    console.log("VERSION: Signals2");

    //Polling mode
    /*console.log("PollingMode");
    setInterval(function(){
        $.get( "/test.json", function( data ) {
            graph =  data ;
            console.log(graph);
            drawGraph(graph);
        });
    }, 500000);

    $.get( "/test.json", function( data ) {
            graph =  data ;
            console.log(graph);
            drawGraph(graph);
        });
    */

    function drawGraph(graph)
    {
        context.clearRect(0, 0, canvas.width, canvas.height);

        var margin  = 20;
        var width = canvas.width;
        var height = canvas.height;

        var cell_size_h = (height - 2*margin) / graph.size[0];
        var cell_size_w = (width - 2*margin) / graph.size[1];

        var cell_size = Math.min(cell_size_h , cell_size_w);

        for (var k in graph.map){
            if (graph.map.hasOwnProperty(k)) {
                var node = k;
                var walls = graph.map[k];

                node = node.replace(/\(/g,'');
                node = node.replace(/\)/g,'');
                node = node.replace(/\ /g,'');
                node = node.split(",");
                
                node[0] = graph.size[0] - parseInt(node[0],10) - 1;
                node[1] = parseInt(node[1],10);
                
                drawCell( node[0], node[1], walls, cell_size, margin );
            }
        }

        drawPlan(graph.plan,graph.size[0],cell_size,margin);

        drawImages(graph.signals,cell_size,margin);

        drawRobot(graph.size[0] - graph.location[0] - 1,graph.location[1],graph.location[2],cell_size,margin);
        
    }

    function drawCell(row,col,walls,cell_size,margin )
    {
        var topLeftX = margin + (cell_size * (col) );
        var topLeftY = margin + (cell_size * (row) );

        var botRightX = margin + (cell_size * (col + 1) );
        var botRightY = margin + (cell_size * (row + 1) );

        var topRightX = margin + (cell_size * (col + 1) );
        var topRightY = margin + (cell_size * (row) );

        var botLeftX = margin + (cell_size * (col) );
        var botLeftY = margin + (cell_size * (row + 1) );

        //Top wall
        if(walls[0] == 1)
        {
            context.beginPath();
            context.moveTo(topLeftX, topLeftY);
            context.lineTo(topRightX, topRightY);
            context.stroke();
        }
        //Left wall
        if(walls[1] == 1)
        {
            context.beginPath();
            context.moveTo(topLeftX, topLeftY);
            context.lineTo(botLeftX, botLeftY);
            context.stroke();
        }
        //Bot wall
        if(walls[2] == 1)
        {
            context.beginPath();
            context.moveTo(botLeftX, botLeftY);
            context.lineTo(botRightX, botRightY);
            context.stroke();
        }
        //Right wall
        if(walls[3] == 1)
        {
            context.beginPath();
            context.moveTo(topRightX, topRightY);
            context.lineTo(botRightX, botRightY);
            context.stroke();
        }
    }

    function drawRobot(row,col,ori,cell_size,margin)
    {
        var centerX = margin + (cell_size * (col) ) + cell_size / 2;
        var centerY = margin + (cell_size * (row) ) + cell_size / 2;
        var radius = cell_size / 3;
        var startAngle = 5* Math.PI / 4 - ori * (Math.PI / 2) ;
        var endAngle = startAngle + Math.PI / 2;

        context.beginPath();
        context.lineWidth = 1;
        context.strokeStyle = '#000000';
        context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
        context.stroke();

        context.beginPath();
        context.lineWidth = 1;
        context.strokeStyle = '#000000';
        context.arc(centerX, centerY, radius, startAngle, endAngle, false);
        context.closePath();
        context.stroke();
    }

    function drawPlan(plan,size,cell_size,margin)
    {
        var last_step = null;
        var last_row = null;
        var last_col = null;
        var centerLastX = null;
        var centerLastY = null;

        for (var step in plan){

            step = plan[step];
            var row = size - step[0] -1;
            var col = step[1];
            var centerNextX = margin + (cell_size * (col) ) + cell_size / 2;
            var centerNextY = margin + (cell_size * (row) ) + cell_size / 2;

            if(last_step !== null)
            {
                context.beginPath();
                context.moveTo(centerLastX, centerLastY);
                context.lineTo(centerNextX, centerNextY);
                context.lineWidth = 5;
                context.strokeStyle = "rgba(0, 255, 0, 0.2)";
                context.stroke();
            }
            
            last_step = step;
            last_row = row;
            last_col = col;
            centerLastX = centerNextX;
            centerLastY = centerNextY;
        }
    }

    function drawImages(signals,cell_size,margin)
    {
        for (var img in signals){

            if (signals.hasOwnProperty(img)) {
                var node = img;
                var str_img = signals[img];

                node = node.replace(/\(/g,'');
                node = node.replace(/\)/g,'');
                node = node.replace(/\ /g,'');
                node = node.split(",");
                
                node[0] = graph.size[0] - parseInt(node[0],10) - 1;
                node[1] = parseInt(node[1],10);
                node[2] = parseInt(node[2],10);
                
                drawImage(str_img,node[0],node[1],node[2],cell_size,margin);

            }

            
        }
        
    }

    function drawImage(image,row,col,ori,cell_size,margin)
    {
        img_name = '';
        if(image == "tr")
            img_name = 'turn_right.jpg';
        if(image == "tl")
            img_name = 'turn_left.jpg';
        if(image == "dtr")
            img_name = 'dont_turn_right.jpg';
        if(image == "dtl")
            img_name = 'dont_turn_left.jpg';

        var imgX = margin + (cell_size * (col) );
        var imgY = margin + (cell_size * (row) );

        var imageObj = new Image();
        imageObj.onload = function() {
            context.translate(imgX+ cell_size / 2, imgY+ cell_size / 2);
            context.rotate( - Math.PI / 2 * ori);
            context.drawImage(imageObj, 0-cell_size/2+margin*2, 0-cell_size/2+margin*2,cell_size-4*margin,cell_size-4*margin);
            context.setTransform(1, 0, 0, 1, 0, 0);
        };
        imageObj.src = img_name;

        
    }

});