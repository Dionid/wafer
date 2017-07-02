//
//  ViewController.swift
//  WaferApp
//
//  Created by Dmitry Levin on 02.07.2017.
//  Copyright © 2017 wafer. All rights reserved.
//

import UIKit
import Alamofire

class ViewController: UIViewController {
    
    var getAccessButton: UIButton!
    var useTrafficButton: UIButton!
    var statusLabel: UILabel!
    var serverIP = "http://34.208.247.57:8484"
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        let buttonFrameSize = CGSize(width: 240, height: 60)
        
        let useTrafficButtonFrame = CGRect(origin: CGPoint(x: (view.bounds.size.width - buttonFrameSize.width)/2, y: view.bounds.size.height - buttonFrameSize.height - 30), size: buttonFrameSize)
        
        let useTrafficButton = UIButton(frame: useTrafficButtonFrame)
        useTrafficButton.setTitle("Use 10 mb traffic", for: .normal)
        
        useTrafficButton.backgroundColor = UIColor.darkGray
        useTrafficButton.addTarget(self, action: #selector(useTraffic10mb), for: .touchUpInside)
        view.addSubview(useTrafficButton)
        self.useTrafficButton = useTrafficButton
        
        let getAccessButtonFrame = CGRect(origin: CGPoint(x: (view.bounds.size.width - buttonFrameSize.width)/2, y: view.bounds.size.height - buttonFrameSize.height*2  - 30*2), size: buttonFrameSize)
        
        let getAccessButton = UIButton(frame: getAccessButtonFrame)
        getAccessButton.setTitle("Get access", for: .normal)
        getAccessButton.backgroundColor = UIColor.darkGray
        getAccessButton.addTarget(self, action: #selector(getAccess), for: .touchUpInside)
        view.addSubview(getAccessButton)
        self.useTrafficButton = getAccessButton
        
        let statusLabelFrameSize = CGSize(width: view.bounds.size.width, height: 30)
        
        let statusLabelFrame = CGRect(origin: CGPoint(x: (view.bounds.size.width - statusLabelFrameSize.width)/2, y: (view.bounds.size.height - buttonFrameSize.height*2 - 30*2)/2), size: statusLabelFrameSize)
        
        let statusLabel = UILabel(frame: statusLabelFrame)
        statusLabel.text = "Try to get access"
        statusLabel.font = UIFont.systemFont(ofSize: 28, weight: UIFontWeightLight)
        statusLabel.textAlignment = .center
        view.addSubview(statusLabel)
        self.statusLabel = statusLabel
        
        
    }
    
    func proceedResponse(_ response: DefaultDataResponse) {
        
        if response.response!.statusCode == 200 {
            self.changeLabel("GO!", UIColor.green)
            
        } else if response.response!.statusCode == 201 {
            self.changeLabel("Please, wait", UIColor.orange)
        } else {
            if let data = response.data, let utf8Text = String(data: data, encoding: .utf8) {
                self.changeLabel(utf8Text, UIColor.red)
            }
        }
        
        
    }
    
    func changeLabel(_ text: String, _ color: UIColor) {
        statusLabel.text = text
        statusLabel.textColor = color
    }
    
    func getAccess() {
        let parameters = ["mac": UIDevice.current.identifierForVendor!.hashValue]
        Alamofire.request(serverIP+"/request", parameters: parameters).response {  response in
            self.proceedResponse(response)
        }
        
    }
    
    func useTraffic10mb() {
        let parameters = ["mac": UIDevice.current.identifierForVendor!.hashValue,
                        "amount": 10]
        Alamofire.request(serverIP+"/use_traffic", parameters: parameters).response {  response in
            self.proceedResponse(response)
        
        }
        
    }
    
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}

