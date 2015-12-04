function cytoscapeDemoViewModel(){
  'use strict'

  var self = this

  self.isReady = ko.observable(false);

  var cy = cytoscape({

    container: $('#cy'),

    elements: [
    {
      data: { id: 'var1',
              label: 'CRUSH_UCDC\n\nsni_sexanalreceptivecondomcnt1',
              conversion_node: true,
              row: 1,
              col:1
            }
    },
    {
      data: { id: 'var2',
              label: 'CRUSH_UCDC\n\nsni_sexanalreceptivecnt1',
              conversion_node: true,
              row: 3,
              col:1
            }
    },
    {
      data: { id: 'var3',
              label: 'CRUSH_UCDC\n\nsni_sexanalinsertivecondomcnt1',
              conversion_node: true,
              row: 4,
              col:1
            }
    },
    {
      data: { id: 'var4',
              label: 'CRUSH_UCDC\n\nsni_sexanalinsertivecnt1',
              conversion_node: true,
              row: 6,
              col:1
            }
    },
    {
      data: { id: 'var5',
              label: 'CRUSH_UCDC\n\nsni_vaginalreceptivecondomcnt1',
              conversion_node: true,
              row: 8,
              col:1
            }
    },
    {
      data: { id: 'var6',
              label: 'CRUSH_UCDC\n\nsni_vaginalreceptivecnt1',
              conversion_node: true,
              row: 10,
              col:1
            }
    },
    {
      data: { id: 'var7',
              label: 'CRUSH_UCDC\n\nsni_vaginalinsertivecondomcnt1',
              conversion_node: true,
              row: 11,
              col:1
            }
    },
    {
      data: { id: 'var8',
              label: 'CRUSH_UCDC\n\nsni_vaginalinsertivecnt1',
              conversion_node: true,
              row: 13,
              col:1
            }
    },
    {
      data: { id: 'divide1',
              label: 'divide',
              row: 2,
              col: 2
            }
    },
    {
      data: { id: 'divide2',
              label: 'divide',
              row: 5,
              col: 2
            }
    },
    {
      data: { id: 'divide3',
              label: 'divide',
              row: 9,
              col: 2
            }
    },
    {
      data: { id: 'divide4',
              label: 'divide',
              row: 12,
              col: 2
            }
    },
    {
      data: { id: 'multiply1',
              label: 'multiply',
              row: 2,
              col: 3
            }
    },
    {
      data: { id: 'multiply2',
              label: 'multiply',
              row: 5,
              col: 3
            }
    },
    {
      data: { id: 'multiply3',
              label: 'multiply',
              row: 9,
              col: 3
            }
    },
    {
      data: { id: 'multiply4',
              label: 'multiply',
              row: 12,
              col: 3
            }
    },
    {
      data: { id: 'conversion1',
              label: '100',
              conversion_node: true,
              row: 1,
              col: 4
            }
    },
    {
      data: { id: 'conversion2',
              label: '100',
              conversion_node: true,
              row: 4,
              col: 4
            }
    },
    {
      data: { id: 'conversion3',
              label: '100',
              conversion_node: true,
              row: 8,
              col: 4
            }
    },
    {
      data: { id: 'conversion4',
              label: '100',
              conversion_node: true,
              row: 11,
              col: 4
            }
    },
    {
      data: { id: 'condition1',
              label: '== 100',
              evaluation_node: true,
              row: 2,
              col: 4,
            }
    },
    {
      data: { id: 'condition2',
              label: '== 100',
              evaluation_node: true,
              row: 5,
              col: 4
            }
    },
    {
      data: { id: 'condition3',
              label: '== 100',
              evaluation_node: true,
              row: 9,
              col: 4 }
    },
    {
      data: { id: 'condition4',
              label: '== 100',
              evaluation_node: true,
              row: 12,
              col: 4
            }
    },

    {
      data: { id: 'all_condition',
              label: 'all',
              conditional_operator: true,
              row: 7,
              col: 5
            }
    },
    {
      data: { id: 'maps_to',
              label: '1: Yes',
              conversion_node: true,
              row: 7,
              col: 6
            }
    },
    {
      data: { id: 'edge1',
              source: 'divide1',
              target: 'multiply1'
            }
    },
    {
      data: { id: 'edge2',
              source: 'condition1',
              target: 'all_condition',
              edge_dotted: true
            }
    },
    {
      data: { id: 'edge3',
              source: 'conversion1',
              target: 'multiply1'
            }
    },
    {
      data: { id: 'edge4',
              source: 'all_condition',
              target: 'maps_to',
              label: 'Maps to'
            }
    },
    {
      data: { id: 'edge5',
              source: 'var1',
              target: 'divide1'
            }
    },
    {
      data: { id: 'edge6',
              source: 'divide1',
              target: 'var2'
            }
    },
    {
      data: { id: 'edge7',
              source: 'multiply1',
              target: 'condition1'
            }
    },
    {
      data: { id: 'edge8',
              source: 'var3',
              target: 'divide2'
            }
    },
    {
      data: { id: 'edge9',
              source: 'divide2',
              target: 'var4'
            }
    },
    {
      data: { id: 'edge10',
              source: 'divide2',
              target: 'multiply2'
            }
    },
    {
      data: { id: 'edge11',
              source: 'conversion2',
              target: 'multiply2'
            }
    },
    {
      data: { id: 'edge12',
              source: 'multiply2',
              target: 'condition2'
            }
    },
    {
      data: { id: 'edge13',
              source: 'condition2',
              target: 'all_condition',
              edge_dotted: true
            }
    },
    {
      data: { id: 'edge14',
              source: 'var5',
              target: 'divide3'
            }
    },
    {
      data: { id: 'edge15',
              source: 'divide3',
              target: 'var6'
            }
    },
    {
      data: { id: 'edge16',
              source: 'var7',
              target: 'divide4'
            }
    },
    {
      data: { id: 'edge17',
              source: 'divide4',
              target: 'var8'
            }
    },
    {
      data: { id: 'edge18',
              source: 'divide3',
              target: 'multiply3'
            }
    },
    {
      data: { id: 'edge19',
              source: 'divide4',
              target: 'multiply4'
            }
    },
    {
      data: { id: 'edge20',
              source: 'conversion3',
              target: 'multiply3'
            }
    },
    {
      data: { id: 'edge21',
              source: 'conversion4',
              target: 'multiply4'
            }
    },
    {
      data: { id: 'edge22',
              source: 'multiply3',
              target: 'condition3'
            }
    },
    {
      data: { id: 'edge23',
              source: 'multiply4',
              target: 'condition4'
            }
    },
    {
      data: { id: 'edge24',
              source: 'condition3',
              target: 'all_condition',
              edge_dotted: true
            }
    },
    {
      data: { id: 'edge25',
              source: 'condition4',
              target: 'all_condition',
              edge_dotted: true
            }
    }
  ],

  style: [
    {
      selector: 'node',
      style: {
        'content': 'data(label)',
        'text-valign': 'center',
        'background-color': '#ffe5e5',
        'color': 'black',
        'border-color': 'black',
        'border-width': 3,
        'shape': 'circle',
        'padding-left': 20,
        'padding-right': 20,
        'padding-top': 40,
        'padding-bottom': 40,
        'width': 'label',
        'height': 'label',
        'font-size': 22,
        'text-wrap': 'wrap'
      }
    },
    {
      selector: '[conditional_operator]',
      style: {
        'content': 'data(label)',
        'shape': 'diamond',
        'background-color': '#ffe5e5',
        'padding-left': 40,
        'padding-right': 40,
        'padding-top': 40,
        'padding-bottom': 40,
      }
    },
    {
      selector: '[conversion_node]',
      style: {
        'content': 'data(label)',
        'shape': 'square',
        'background-color': '#e5f2ff',
        'padding-top': 20,
        'padding-bottom': 20
      }
    },
    {
      selector: '[evaluation_node]',
      style: {
        'content': 'data(label)',
        'shape': 'square',
        'background-color': '#ffe5e5',
        'padding-top': 20,
        'padding-bottom': 20
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 3,
        'target-arrow-shape': 'triangle',
        'source-arrow-shape': 'circle',
        'line-color': '#000000',
        'target-arrow-color': '#cc0000',
        'source-arrow-color': 'blue',
        'content': 'data(label)',
        'text-outline-width': 2,
        'color': 'white'
      }
    },
    {
      selector: '[edge_dotted]',
      style:{
        'line-style': 'dotted'
      }
    }
  ],

  layout: {
    name: 'grid',
    rows: 13,
    columns: 6,
    position: function(node){
      return {row:node.data('row'), col:node.data('col')};
    }
  },
});

cy.ready(function(){
  cy.autolock(true);
  cy.zoomingEnabled(false);
  cy.panningEnabled(false);
  self.isReady(true);
})
}




var CANVAS = document.createElement('canvas');

$('#export-png').click(function(){
  var cy = $('#cy').cytoscape('get');
  var width = cy.width();
  var height = cy.height();
  var image = cy.png({bg: 'white'});
  var imgObj = new Image();
  imgObj.src = image;

  CANVAS.width = width;
  CANVAS.height = height;
  context = CANVAS.getContext('2d');
  context.drawImage(imgObj, 0, 0, width, height);

  CANVAS.toBlob(function(blob) {
    saveAs(blob, 'imputation.png');
  });
  context.clearRect(0,0, width, height)
})

$('#export-json').click(function(){
  var cy = $('#cy').cytoscape('get');
  json_file = cy.json();
  var blob = new Blob(
    [JSON.stringify(json_file, false, '\t')], {type: "application/json"});
  saveAs(blob, 'imputation.json');
})