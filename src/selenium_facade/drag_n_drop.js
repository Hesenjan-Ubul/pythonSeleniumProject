function simulateDragDrop(sourceNode, destinationNode, x, y) {
  var EVENT_TYPES = {
    DRAG_END: "dragend",
    DRAG_START: "dragstart",
    DROP: "drop",
  };

  function createCustomEvent(type) {
    var event = new CustomEvent("CustomEvent");
    event.initCustomEvent(type, true, true, null);
    event.dataTransfer = {
      data: {},
      setData: function (type, val) {
        this.data[type] = val;
      },
      getData: function (type) {
        return this.data[type];
      },
    };
    return event;
  }

  function dispatchEvent(node, type, event) {
    if (node.dispatchEvent) {
      return node.dispatchEvent(event);
    }
    if (node.fireEvent) {
      return node.fireEvent("on" + type, event);
    }
  }

  var dataTransfer = new DataTransfer();
  var event = createCustomEvent(EVENT_TYPES.DRAG_START);
  event.dataTransfer = dataTransfer;
  dispatchEvent(sourceNode, EVENT_TYPES.DRAG_START, event);
  var dropEvent = new DragEvent("drop", {
    dataTransfer,
    bubbles: true,
    cancelable: true,
    screenX: x,
    screenY: y,
    clientX: x,
    clientY: y,
  });

  dispatchEvent(destinationNode, EVENT_TYPES.DROP, dropEvent);

  var dragEndEvent = createCustomEvent(EVENT_TYPES.DRAG_END);
  dragEndEvent.dataTransfer = event.dataTransfer;
  dispatchEvent(sourceNode, EVENT_TYPES.DRAG_END, dragEndEvent);
}

simulateDragDrop(arguments[0], arguments[1], arguments[2], arguments[3]);
