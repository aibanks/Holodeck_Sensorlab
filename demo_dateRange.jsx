() => {
    const [startDate, setStartDate] = useState(new Date( __variableContainingTheLowestDateOfCurrentQuery__));  
    const [endDate, setEndDate] = useState(new Date(__variableContainingTheHighestDateOfCurrentQuery__));
    return (
      <>
        <DatePicker
          selected={startDate}
          onChange={(date) => setStartDate(date)}
          selectsStart
          startDate={startDate}
          endDate={endDate}
        />
        <DatePicker
          selected={endDate}
          onChange={(date) => setEndDate(date)}
          selectsEnd
          startDate={startDate}
          endDate={endDate}
          minDate={startDate}
        />
      </>
    );
  };
