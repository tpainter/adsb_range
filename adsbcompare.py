if __name__ == "__main__":
    from twisted.internet import reactor
    from history import History
    from history import allHistory
    
    #TODO get connection information from file
    #Lines of the file are: [Name] [IP] [PORT] 
    
    connections = [["Laptop1", "192.168.0.100", 30010, ],
                    ["Laptop2", "192.168.0.100", 30011, ],
                    ["Laptop3", "192.168.0.100", 30012, ],
                    ["Laptop4", "192.168.0.100", 30013, ],
                                                        ]
    
    for i in connections:
        History(i[0], i[1], i[2])
    
    
    #Write first results after only 1 minute
    reactor.callLater(60, allHistory)
    reactor.run()