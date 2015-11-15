var CANVAS = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));

var operatorNode = function(posX, posY, label, fillColor){
  return new joint.shapes.basic.Circle({
    position: { x: posX, y: posY },
    attrs: { text: { text: label, 'font-size': 12, 'font-family': 'arial' },
             circle: { fill: fillColor } },
    });
}

var conversionNode = function(posX, posY, label, fillColor, textFillColor){
  var rect_size = calculateHeightWidth(label);
  return new joint.shapes.basic.Rect({
    position: { x: posX, y: posY },
    size: { width: rect_size.width, height: rect_size.height },
    attrs: { rect: { fill: fillColor },
             text: { text: label, fill: textFillColor, 'font-size': 12,
                     'font-family': 'arial' } }
  })
}

var createLabel = function(txt, position) {
  return {
      labels: [{ position: position, attrs: { text: { text: txt }}}]
  };
};

var createEdge = function(sourceID, targetID, attrs) {
  return new joint.dia.Link({
    source: { id: sourceID },
    target: { id: targetID },
    attrs: attrs
  });
}

var calculateHeightWidth = function(label){
  var maxLineLength = 2
  var letterSize = 8;
  var width = getTextWidth(label);
  var height = 2 * ((label.split('\n').length + 1) * letterSize);

  return {width: width, height: height};
}

/**
 * Uses canvas.measureText to compute and return the width of the given text of given font in pixels.
 *
 * @param text The text to be rendered.
 * @param {String} font The css font descriptor that text is to be rendered with (e.g. "14px verdana").
 *
 * @see http://stackoverflow.com/questions/118241/calculate-text-width-with-javascript/21015393#21015393
 */
function getTextWidth(text) {
    var font = '12pt arial' //maybe not hard-code this
    var slicedText = text.split('\n');
    var text = slicedText.sort(function (a, b) { return b.length - a.length; })[0];
    var context = CANVAS.getContext("2d");
    context.font = font;
    var metrics = context.measureText(text);
    return metrics.width;
};

var createGraph = function(){
  var graph = new joint.dia.Graph;

  var paper = new joint.dia.Paper({
    el: $('#ebacImputation'),
    width: 1200,
    height: 1200,
    model: graph,
    gridSize: 1,
    interactive: false
  });
//******************************************************************************
edgeAttrsDotted = {
      '.marker-target': { fill: '#4b4a67', stroke: '#4b4a67', d: 'M 10 0 L 0 5 L 10 10 z' },
       '.connection': { 'stroke-dasharray': '2,5' }
    }

edgeAttrs = {
      '.marker-target': { fill: '#4b4a67', stroke: '#4b4a67', d: 'M 10 0 L 0 5 L 10 10 z' }
    }
//******************************************************************************
  var receptiveCondom1 = conversionNode(
    0, 0,
    'CRUSH_UCDC\n\nsni_sexanalreceptivecondomcnt1',
    '#e5f2ff', '#000000');

  var receptive1 = conversionNode(
    0, 80,
    'CRUSH_UCDC\n\nsni_sexanalreceptivecnt1',
    '#e5f2ff', '#000000');

  var receptiveMultiplier1 = conversionNode(
    485, 30,
    '100',
    '#e5f2ff', '#000000');

  var operator1 = operatorNode(300, 35, 'divide', '#ffe5e5');
  var operator2 = operatorNode(390, 55, 'multiply', '#ffe5e5');

  var edge1 = createEdge(receptiveCondom1.id, operator1.id, edgeAttrs);
  var edge2 = createEdge(operator1.id, receptive1.id, edgeAttrs);
  var edge3 = createEdge(operator1.id, operator2.id, edgeAttrs);
  var edge4 = createEdge(receptiveMultiplier1.id, operator2.id, edgeAttrs);
//******************************************************************************
  var insertiveCondom1 = conversionNode(
    0, 170,
    'CRUSH_UCDC\n\nsni_sexanalinsertivecondomcnt1',
    '#e5f2ff', '#000000');

  var insertive1 = conversionNode(
    0, 250,
    'CRUSH_UCDC\n\nsni_sexanalinsertivecnt1',
    '#e5f2ff', '#000000');

  var insertiveMultiplier1 = conversionNode(
    485, 200,
    '100',
    '#e5f2ff', '#000000');

  var operator3 = operatorNode(300, 205, 'divide', '#ffe5e5');
  var operator4 = operatorNode(390, 225, 'multiply', '#ffe5e5');

  var edge5 = createEdge(insertiveCondom1.id, operator3.id, edgeAttrs);
  var edge6 = createEdge(operator3.id, insertive1.id, edgeAttrs);
  var edge7 = createEdge(operator3.id, operator4.id, edgeAttrs);
  var edge8 = createEdge(insertiveMultiplier1.id, operator4.id, edgeAttrs);
//******************************************************************************
  var vaginalReceptiveCondom1 = conversionNode(
    0, 340,
    'CRUSH_UCDC\n\nsni_vaginalreceptivecondomcnt1',
    '#e5f2ff', '#000000');

  var vaginalReceptive1 = conversionNode(
    0, 420,
    'CRUSH_UCDC\n\nsni_vaginalreceptivecnt1',
    '#e5f2ff', '#000000');

  var vaginalReceptiveMultiplier1 = conversionNode(
    485, 365,
    '100',
    '#e5f2ff', '#000000');

  var operator5 = operatorNode(300, 370, 'divide', '#ffe5e5');
  var operator6 = operatorNode(390, 390, 'multiply', '#ffe5e5');

  var edge9 = createEdge(vaginalReceptiveCondom1.id, operator5.id, edgeAttrs);
  var edge10 = createEdge(operator5.id, vaginalReceptive1.id, edgeAttrs);
  var edge11 = createEdge(operator5.id, operator6.id, edgeAttrs);
  var edge12 = createEdge(vaginalReceptiveMultiplier1.id, operator6.id, edgeAttrs);
//******************************************************************************
  var vaginalInsertiveCondom1 = conversionNode(
    0, 510,
    'CRUSH_UCDC\n\nsni_vaginalinsertivecondomcnt1',
    '#e5f2ff', '#000000');

  var vaginalInsertive1 = conversionNode(
    0, 590,
    'CRUSH_UCDC\n\nsni_vaginalinsertivecnt1',
    '#e5f2ff', '#000000');

  var vaginalInsertiveMultiplier1 = conversionNode(
    485, 530,
    '100',
    '#e5f2ff', '#000000');

  var operator7 = operatorNode(300, 535, 'divide', '#ffe5e5');
  var operator8 = operatorNode(390, 555, 'multiply', '#ffe5e5');

  var edge13 = createEdge(vaginalInsertiveCondom1.id, operator7.id, edgeAttrs);
  var edge14 = createEdge(operator7.id, vaginalInsertive1.id, edgeAttrs);
  var edge15 = createEdge(operator7.id, operator8.id, edgeAttrs);
  var edge16 = createEdge(vaginalInsertiveMultiplier1.id, operator8.id, edgeAttrs);
//******************************************************************************
  var diamond = new joint.shapes.basic.Path({
      size: { width: 60, height: 60 },
      position: { x: 850, y: 300 },
      attrs: {
          path: { d: 'M 30 0 L 60 30 30 60 0 30 z', fill: '#ffe5e5' },
          text: {
              text: 'All',
              'ref-y': .4
          }
      }
  });

  var rule1 = conversionNode(550, 65, ' == 100 ', '#ffe5e5', '#000000');
  var rule2 = conversionNode(550, 235, ' == 100 ', '#ffe5e5', '#000000');
  var rule3 = conversionNode(550, 400, ' == 100 ', '#ffe5e5', '#000000');
  var rule4 = conversionNode(550, 565, ' == 100 ', '#ffe5e5', '#000000');

  var edge17 = createEdge(operator2.id, rule1.id, edgeAttrsDotted);
  var edge18 = createEdge(operator4.id, rule2.id, edgeAttrsDotted);
  var edge19 = createEdge(operator6.id, rule3.id, edgeAttrsDotted);
  var edge20 = createEdge(operator8.id, rule4.id, edgeAttrsDotted);

  var edge21 = createEdge(rule1.id, diamond.id, edgeAttrsDotted);
  var edge22 = createEdge(rule2.id, diamond.id, edgeAttrsDotted);
  var edge23 = createEdge(rule3.id, diamond.id, edgeAttrsDotted);
  var edge24 = createEdge(rule4.id, diamond.id, edgeAttrsDotted);

  var mapsTo = conversionNode(1000, 313, ' 1 - Yes ', '#ffffff');

  var edge25 = createEdge(diamond.id, mapsTo.id, edgeAttrs);
  edge25.set(createLabel('Maps to', 0.5))

  graph.addCells([receptiveCondom1, receptive1, operator1, edge1, edge2,
                  operator2, edge3, receptiveMultiplier1, edge4,
                  insertiveCondom1, insertive1, insertiveMultiplier1,
                  operator3, operator4, edge5, edge6, edge7, edge8,
                  vaginalReceptiveCondom1, vaginalReceptive1, vaginalReceptiveMultiplier1,
                  operator5, operator6, edge9, edge10, edge11, edge12,
                  rule1, rule2, rule3, edge17, edge18, edge19,
                  vaginalInsertiveCondom1, vaginalInsertive1, vaginalInsertiveMultiplier1,
                  operator7, operator8, edge13, edge14, edge15, edge16,
                  rule4, edge20, diamond, edge21, edge22, edge23, edge24, mapsTo,
                  edge25]);

  paper.fitToContent();
  console.log('Paper width: ' + paper.options.width);
  console.log('Paper height: ' + paper.options.height);
}