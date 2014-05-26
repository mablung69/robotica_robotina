$(function () {

    console.log(".---------------------------.");
    console.log("| *   Starting Robotina   * |");
    console.log("'---------------------------'");

    var canvas = document.getElementById('myCanvas');
    var context = canvas.getContext('2d');
    var graph = null;

    $.get( "/test.json", function( data ) {
        graph =  data ;
        console.log(graph);
        drawGraph(graph);
    });

    function drawGraph(graph)
    {

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

        console.log(cell_size);

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

});