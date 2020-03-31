package main

import (
	"encoding/gob"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	qrcodeTerminal "github.com/mdp/qrterminal/v3"
	whatsapp "github.com/Rhymen/go-whatsapp"
)

// var mainApi = "https://covid19-api.yggdrasil.id%s"
var mainApi = "http://localhost:5001"
var userAgent = "gobot-covid19/3.0"

type waHandler struct {
	c         *whatsapp.Conn
	startTime uint64
}

func (wh *waHandler) HandleTextMessage(message whatsapp.TextMessage) {
	if !strings.Contains(strings.ToLower(message.Text), "!covid") || message.Info.Timestamp < wh.startTime {
		return
	}

	reply := "timeout"
	waitSec := rand.Intn(4-2)+2
	param := "/"
	log.Printf("Randomly paused %d for throtling", waitSec)
	time.Sleep(time.Duration(waitSec) * time.Second)

	command := strings.Fields(message.Text)
	if len(command) > 1{
		for index := range command[1:] {
			param += command[index+1]
		}
	}

	link := fmt.Sprintf(mainApi + "%s", param)

	body, err:= reqUrl(link)
	if err >= 400 {
		log.Printf("Error, %d when access %s ", err, link)
		return
	}
	var result map[string]interface {}

	jsonErr := json.Unmarshal(body, &result)
	if jsonErr != nil {
		log.Fatalf("Break point 4 %s %s", jsonErr, result)
	}

	messages := result["messages"]
	// images := result["images"].([]interface{})
	// files := result["files"].([]interface{})

	reply = messages.(string)

	if reply != "timeout" {
		go sendMessage(wh.c, reply, message.Info.RemoteJid)
	}
}

func main() {
	//create new WhatsApp connection
	wac, err := whatsapp.NewConn(5 * time.Second)
	wac.SetClientVersion(0, 4, 2080)
	if err != nil {
		log.Fatalf("error creating connection: %v\n", err)
	}

	//Add handler
	wac.AddHandler(&waHandler{wac, uint64(time.Now().Unix())})

	//login or restore
	if err := login(wac); err != nil {
		log.Fatalf("error logging in: %v\n", err)
	}

	//verifies phone connectivity
	pong, err := wac.AdminTest()

	if !pong || err != nil {
		log.Fatalf("error pinging in: %v\n", err)
	}

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c

	//Disconnect safe

	fmt.Println("Shutting down now.")
	session, err := wac.Disconnect()
	if err != nil {
		log.Fatalf("error disconnecting: %v\n", err)
	}
	if err := writeSession(session); err != nil {
		log.Fatalf("error saving session: %v", err)
	}
}

func sendMessage(wac *whatsapp.Conn, message string, RJID string) {
	msg := whatsapp.TextMessage{
		Info: whatsapp.MessageInfo{
			RemoteJid: RJID,
		},
		Text: message,
	}

	msgId, err := wac.Send(msg)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error sending message: %v", err)
		os.Exit(1)
	} else {
		fmt.Println("Message Sent -> ID : " + msgId)
	}
}

func login(wac *whatsapp.Conn) error {
	//load saved session
	session, err := readSession()
	if err == nil {
		//restore session
		session, err = wac.RestoreWithSession(session)
		if err != nil {
			return fmt.Errorf("restoring failed: %v\n", err)
		}
	} else {
		//no saved session -> regular login
		qr := make(chan string)
		go func(){
			config := qrcodeTerminal.Config{
				Level: qrcodeTerminal.L,
				Writer: os.Stdout,
				BlackChar: qrcodeTerminal.BLACK,
				WhiteChar: qrcodeTerminal.WHITE,
				QuietZone: 1,
			}
			qrcodeTerminal.GenerateWithConfig(<-qr, config)
		}()
		session, err = wac.Login(qr)
		if err != nil {
			return fmt.Errorf("error during login: %v\n", err)
		}
	}

	//save session
	err = writeSession(session)
	if err != nil {
		return fmt.Errorf("error saving session: %v\n", err)
	}
	return nil
}

func readSession() (whatsapp.Session, error) {
	session := whatsapp.Session{}
	log.Println("Trying to get the session " + getSessionName())
	file, err := os.Open(getSessionName())
	if err != nil {
		return session, err
	}
	defer file.Close()
	decoder := gob.NewDecoder(file)
	err = decoder.Decode(&session)
	if err != nil {
		return session, err
	}
	return session, nil
}

func writeSession(session whatsapp.Session) error {
	file, err := os.Create(getSessionName())
	if err != nil {
		return err
	}
	defer file.Close()
	encoder := gob.NewEncoder(file)
	err = encoder.Encode(session)
	if err != nil {
		return err
	}
	return nil
}

func getSessionName() string {
	mydir, err := os.Getwd()
	if err != nil {
		fmt.Println(err)
	}
	if _, err := os.Stat(mydir + "/session"); os.IsNotExist(err) {
		os.MkdirAll(mydir+"/session", os.ModePerm)
	}
	sessionName := ""
	if len(os.Args) == 1 {
		sessionName = mydir + "/session" + "/whatsappSession.gob"
	} else {
		sessionName = mydir + "/session/" + os.Args[1] + ".gob"
	}

	return sessionName
}

//HandleError needs to be implemented to be a valid WhatsApp handler
func (h *waHandler) HandleError(err error) {
	if e, ok := err.(*whatsapp.ErrConnectionFailed); ok {
		log.Printf("Connection failed, underlying error: %v", e.Err)
		log.Println("Waiting 30sec...")
		<-time.After(30 * time.Second)
		log.Println("Reconnecting...")
		err := h.c.Restore()
		if err != nil {
			log.Fatalf("Restore failed: %v", err)
		}
	} else {
		log.Printf("error occoured: %v\n", err)
	}
}

func reqUrl(url string) ([]byte, int) {

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Fatalf("Break point 1 %s", err)
	}

	req.Header.Set("User-Agent", "gobot-covid19/3.0")

	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
			log.Fatalln(err)
	}

	if res.StatusCode >= 400 {
		return nil, res.StatusCode
	}

	body, readErr := ioutil.ReadAll(res.Body)
	if readErr != nil {
		log.Fatalf("Break point 3 %s", readErr)
	}

	return body, 200
}


