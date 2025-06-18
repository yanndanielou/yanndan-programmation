/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package cfx00854407.network;

/**
 *
 * @author z003urxb
 */
public interface AFFCARMessage {
    public byte[] getBytes() throws PacketFormatException;
    public void putBytes(byte[] bytes);
}
